from watson.watson import Watson

from sherlockpipe.loading.tool_with_candidate import ToolWithCandidate


class Vetter(ToolWithCandidate):
    watson = None

    def __init__(self, object_dir, vetting_dir, is_candidate_from_search, candidates_df) -> None:
        super().__init__(is_candidate_from_search, candidates_df)
        self.watson = Watson(object_dir, vetting_dir)

    def run(self, cpus, **kwargs):
        self.watson.vetting_with_data(kwargs['candidate'], kwargs['star_df'], kwargs['transits_df'],
                                      cpus, transits_mask=kwargs["transits_mask"],
                                      iatson_enabled=kwargs['iatson_enabled'], iatson_inputs_save=True,
                                      gpt_enabled=kwargs['gpt_enabled'], gpt_api_key=kwargs['gpt_api_key'],
                                      only_summary=kwargs['only_summary'])

    def object_dir(self):
        return self.watson.object_dir
