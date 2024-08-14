import argparse
import json
import logging
import os.path
import sys

from .physspec_wrapper import PhysspecDllWrapper, PREPARE_ERROR_CODES


def calc_physspec(seed, histories):
    # load lib and prepare
    cur_path = os.getcwd()
    lib = PhysspecDllWrapper()
    input_filename = os.path.join(cur_path, 'physspec_input.json')
    error_num = lib.physspec_prepare(input_filename, seed)
    if error_num:
        error_msg = PREPARE_ERROR_CODES[error_num] if error_num < len(PREPARE_ERROR_CODES) else ''
        logging.error(f'Prepare error #{error_num}: {error_msg}')
        sys.exit()
    logging.info('Prepared successfully')

    # calculate
    N = histories * 1000
    logging.info(f'Starting calculation with N={N} and seed={seed}')
    _ = lib.physspec_calculate(N, True)
    # if res != 0:
    #     logging.error(f'Calculation error #{res}')
    #     return

    # save results
    output_filename = os.path.join(cur_path, 'physspec_output.json')
    lib.physspec_save_json(output_filename)

    del lib
    logging.info('done')


def _pretty_output_json(filename):
    with open(filename) as f:
        data = json.load(f)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='physspec -- util for physical spectr calculation with Monte-Carlo method')

    parser.add_argument('-N', '--histories', help='calculation histories, thsnds', type=int,
                        default=1)
    parser.add_argument('-s', '--seed', help='seed for random generator, default=0 <- random seed',
                        type=int, default=0)
    parser.add_argument('-v', '--verbose', help='verbose mode', action="store_true", default=False)
    parser.add_argument('--pretty', help='pretty json output file', action="store_true")

    args = parser.parse_args()

    # logger
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s : %(levelname)s : %(message)s',
        stream=sys.stderr,
    )

    calc_physspec(args.seed, args.histories)

    if args.pretty:
        _pretty_output_json('physspec_output.json')
