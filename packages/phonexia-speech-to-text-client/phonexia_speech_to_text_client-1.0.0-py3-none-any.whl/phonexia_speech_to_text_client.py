#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

import grpc
import soundfile
from google.protobuf.duration_pb2 import Duration
from google.protobuf.json_format import MessageToDict, Parse, ParseError
from phonexia.grpc.common.core_pb2 import (
    Audio,
    RawAudioConfig,
    TimeRange,
)
from phonexia.grpc.technologies.speech_to_text.v1.speech_to_text_pb2 import (
    ListAllowedSymbolsRequest,
    ListAllowedSymbolsResponse,
    RequestedAdditionalWord,
    ResultType,
    TranscribeConfig,
    TranscribeRequest,
    TranscribeResponse,
)
from phonexia.grpc.technologies.speech_to_text.v1.speech_to_text_pb2_grpc import (
    SpeechToTextStub,
)


def print_json(message: dict, output_file: Optional[Path] = None) -> None:
    json.dump(
        message, output_file.open("w") if output_file else sys.stdout, indent=2, ensure_ascii=False
    )


def message_to_dict(message: object) -> dict:
    return MessageToDict(
        message,
        always_print_fields_with_no_presence=True,
        preserving_proto_field_name=True,
        use_integers_for_enums=False,
    )


def time_to_duration(time: float) -> Optional[Duration]:
    if time is None:
        return None
    duration = Duration()
    duration.seconds = int(time)
    duration.nanos = int((time - duration.seconds) * 1e9)
    return duration


def make_transcribe_request(
    file: str,
    preferred_phrases: list[str],
    additional_words: list[RequestedAdditionalWord],
    result_types: list[ResultType],
    start: Optional[float],
    end: Optional[float],
    use_raw_audio: bool,
) -> Iterator[TranscribeRequest]:
    time_range = TimeRange(start=time_to_duration(start), end=time_to_duration(end))
    transcribe_config: TranscribeConfig | None = TranscribeConfig(
        preferred_phrases=preferred_phrases,
        additional_words=additional_words,
        result_types=result_types,
    )
    chunk_size = 1024 * 100
    if use_raw_audio:
        with soundfile.SoundFile(file) as r:
            raw_audio_config = RawAudioConfig(
                channels=r.channels,
                sample_rate_hertz=r.samplerate,
                encoding=RawAudioConfig.AudioEncoding.PCM16,
            )
            for data in r.blocks(blocksize=r.samplerate, dtype="int16"):
                yield TranscribeRequest(
                    audio=Audio(
                        content=data.flatten().tobytes(),
                        raw_audio_config=raw_audio_config,
                        time_range=time_range,
                    ),
                    config=transcribe_config,
                )
                time_range = None
                raw_audio_config = None
                transcribe_config = None

    else:
        with open(file, mode="rb") as fd:
            while chunk := fd.read(chunk_size):
                yield TranscribeRequest(
                    audio=Audio(content=chunk, time_range=time_range),
                    config=transcribe_config,
                )
                time_range = None
                transcribe_config = None


def write_result(response: TranscribeResponse, output_file: Optional[Path] = None) -> None:
    logging.debug(f"Writing transcription to {str(output_file) if output_file else 'stdout'}")
    message = message_to_dict(message=response)
    print_json(message, output_file)


def transcribe(
    channel: grpc.Channel,
    input_file: Path,
    output_file: Optional[Path],
    preferred_phrases: Optional[Path],
    additional_words: Optional[Path],
    return_onebest: bool,
    return_nbest: bool,
    return_confusion_network: bool,
    start: Optional[float],
    end: Optional[float],
    use_raw_audio: bool,
    metadata: Optional[list],
) -> None:
    logging.info(
        "Transcribing {input} -> {output}".format(
            input=input_file, output=(output_file if output_file else "'stdout'")
        )
    )

    result_types: list[ResultType] = []
    if return_nbest:
        result_types.append(ResultType.RESULT_TYPE_N_BEST)
    if return_confusion_network:
        result_types.append(ResultType.RESULT_TYPE_CONFUSION_NETWORK)
    if return_onebest or len(result_types) == 0:
        result_types.append(ResultType.RESULT_TYPE_ONE_BEST)

    preferred_phrases_list: list[str] = []
    if preferred_phrases is not None:
        with open(preferred_phrases) as f:
            preferred_phrases_list = f.read().splitlines()

    additional_words_list: list[RequestedAdditionalWord] = []
    if additional_words is not None:
        with open(additional_words) as f:
            transcribe_config: TranscribeConfig = Parse(text=f.read(), message=TranscribeConfig())
            additional_words_list = transcribe_config.additional_words

    response_it = make_transcribe_request(
        file=input_file,
        preferred_phrases=preferred_phrases_list,
        additional_words=additional_words_list,
        result_types=result_types,
        start=start,
        end=end,
        use_raw_audio=use_raw_audio,
    )

    stub = SpeechToTextStub(channel)
    for response in stub.Transcribe(response_it, metadata=metadata):
        write_result(response, output_file)


def list_allowed_symbols(
    channel: grpc.Channel, output_file: Optional[Path], metadata: Optional[list]
):
    logging.info("Listing allowed symbols")
    stub = SpeechToTextStub(channel)

    logging.debug(f"Writing symbols to {str(output_file) if output_file else 'stdout'}")
    response: ListAllowedSymbolsResponse = stub.ListAllowedSymbols(
        ListAllowedSymbolsRequest(), metadata=metadata
    )

    message = message_to_dict(message=response)
    print_json(message, output_file)


def handle_grpc_error(e: grpc.RpcError):
    logging.error(f"gRPC call failed with status code: {e.code()}")
    logging.error(f"Error details: {e.details()}")

    if e.code() == grpc.StatusCode.UNAVAILABLE:
        logging.error("Service is unavailable. Please try again later.")
    elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
        logging.error("Invalid arguments were provided to the RPC.")
    elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
        logging.error("The RPC deadline was exceeded.")
    else:
        logging.error(f"An unexpected error occurred: {e.code()} - {e.details()}")


def check_file_exists(path: Path) -> Path:
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"File '{path}' does not exist.")
    return Path(path)


def main():
    parser = argparse.ArgumentParser(
        description=("Transcribe speech to text using the Phonexia Speech to Text microservice."),
    )
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        default="localhost:8080",
    )
    parser.add_argument(
        "-l",
        "--log_level",
        type=str,
        default="error",
        choices=["critical", "error", "warning", "info", "debug"],
    )
    parser.add_argument(
        "--metadata",
        metavar="key=value",
        nargs="+",
        type=lambda x: tuple(x.split("=")),
        help="Custom client metadata.",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=check_file_exists,
        help="Output result to a file. If omitted, output to stdout.",
    )
    parser.add_argument(
        "-p",
        "--preferred_phrases",
        type=check_file_exists,
        help="Path to a file containing a list of preferred phrases, each on its separate line.",
    )
    parser.add_argument(
        "-a",
        "--additional_words",
        type=check_file_exists,
        help="Path to a file containing a list of words to be added to the transcription dictionary. "
        "You can generate reference list by running this client with '--example_additional_words' argument.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output result to a file. If omitted, output to stdout.",
    )
    parser.add_argument(
        "--list_allowed_symbols",
        action="store_true",
        help="List graphemes and phonemes allowed for new words.",
    )
    parser.add_argument(
        "--return_onebest",
        action="store_true",
        help="Return onebest transcription result. If no result types are specified, onebest is returned by default.",
    )
    parser.add_argument(
        "--return_nbest", action="store_true", help="Return nbest transcription result."
    )
    parser.add_argument(
        "--return_confusion_network",
        action="store_true",
        help="Return confusion network transcription result.",
    )
    parser.add_argument(
        "--example_additional_words",
        action="store_true",
        help="Generate example additional words list.",
    )
    parser.add_argument("--use_ssl", action="store_true", help="Use SSL connection.")
    parser.add_argument("--start", type=float, help="Audio start time.")
    parser.add_argument("--end", type=float, help="Audio end time.")
    parser.add_argument(
        "--use_raw_audio", action="store_true", help="Send the audio in raw format."
    )

    args = parser.parse_args()

    output_file: Optional[Path] = args.output

    if args.start is not None and args.start < 0:
        raise ValueError("Parameter 'start' must be a non-negative float.")

    if args.end is not None and args.end <= 0:
        raise ValueError("Parameter 'end' must be a positive float.")

    logging.basicConfig(
        level=args.log_level.upper(),
        format="[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        logging.info(f"Connecting to {args.host}")
        channel = (
            grpc.secure_channel(target=args.host, credentials=grpc.ssl_channel_credentials())
            if args.use_ssl
            else grpc.insecure_channel(target=args.host)
        )

        start_time = datetime.now()

        if args.list_allowed_symbols:
            list_allowed_symbols(
                channel=channel,
                output_file=args.output,
                metadata=args.metadata,
            )

        elif args.example_additional_words:
            additional_words = {
                "additional_words": [
                    {
                        "spelling": "frumious",
                        "pronunciations": ["f r u m i o s", "f r u m i u s"],
                    },
                    {
                        "spelling": "flibbertigibbet",
                        "pronunciations": ["f l i b r t i j i b i t", "f l i b r t i j i b e t"],
                    },
                ]
            }
            print_json(additional_words, output_file)

        else:
            if not args.input:
                logging.error("Missing input file")
                exit(1)

            transcribe(
                channel=channel,
                input_file=args.input,
                output_file=output_file,
                preferred_phrases=args.preferred_phrases,
                additional_words=args.additional_words,
                return_onebest=args.return_onebest,
                return_nbest=args.return_nbest,
                return_confusion_network=args.return_confusion_network,
                start=args.start,
                end=args.end,
                use_raw_audio=args.use_raw_audio,
                metadata=args.metadata,
            )

        logging.debug(f"Elapsed time {(datetime.now() - start_time)}")

    except grpc.RpcError as e:
        handle_grpc_error(e)
        exit(1)
    except ParseError as e:
        logging.error(f"Error while parsing additional words list: {e}")  # noqa: TRY400
        exit(1)
    except Exception:
        logging.exception("Unknown error")
        exit(1)


if __name__ == "__main__":
    main()
