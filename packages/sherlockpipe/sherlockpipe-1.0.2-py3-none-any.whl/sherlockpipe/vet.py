from argparse import ArgumentParser

from sherlockpipe.vetting.run import run_vet

if __name__ == '__main__':
    ap = ArgumentParser(description='Vetting of Sherlock objects of interest')
    ap.add_argument('--object_dir', help="If the object directory is not your current one you need to provide the "
                                         "ABSOLUTE path", required=False)
    ap.add_argument('--candidate', type=int, default=None, help="The candidate signal to be used.", required=False)
    ap.add_argument('--ml', action='store_true', default=False, help="Whether tu run WATSON-NET.", required=False)
    ap.add_argument('--properties', help="The YAML file to be used as input.", required=False)
    ap.add_argument('--cpus', type=int, default=None, help="The number of CPU cores to be used.", required=False)
    ap.add_argument('--only_summary', action='store_true', default=False, help="Whether only the summary report should be created.", required=False)
    ap.add_argument('--gpt', action='store_true', default=False, help="Whether the GPT analysis should be run.", required=False)
    ap.add_argument('--gpt_key', type=str, default=None, help="The GPT api key.", required=False)
    args = ap.parse_args()
    run_vet(args.object_dir, args.candidate, args.properties, args.cpus, run_iatson=args.ml, run_gpt=args.gpt, gpt_key=args.gpt_key, only_summary=args.only_summary)
