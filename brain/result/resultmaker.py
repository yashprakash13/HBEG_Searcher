import pandas as pd
from brain.result.result_utils import make_continous_appends_for_df, order_rows_from_df
from utils.constants import (
    AUTHOR_COL_NAME,
    LENGTH_COL_NAME,
    NUM_MAX_RESULT_FETCH,
    STORY_ID_COL_NAME,
)


class ResultMaker:
    def __init__(
        self,
        indexclass_obj,
        type1_title_ids=None,
        type1_author_names=None,
        type1_length_name=None,
        type2_summ_ids=None,
    ):
        self.indexclass_obj = indexclass_obj

        self.type1_title_ids = type1_title_ids
        self.type1_author_names = type1_author_names
        self.type1_length_name = type1_length_name
        self.type2_summ_ids = type2_summ_ids

        # the result dataframe
        self.df_to_return = None

        # start result making
        self._perform_result_making()

    def _perform_result_making(self):
        """
        Start the result making process. This is made up of these rules:
        1. If type2 is not None: return only those results
        2. Otherwise:
            2.1) Apply author and length specified on top of results from titleids
            2.2) If no title ids, then filter by author and/or length
        """

        if self.type2_summ_ids:
            # process number 1 above
            self._do_type2_filtering()

        if not self.type1_title_ids:
            # process number 2.2 above
            self._do_type1_filtering(no_title=True)
        else:
            # process number 2.1 above
            self._do_type1_filtering()

    def _do_type2_filtering(self):
        """type 2 result making"""

        self.df_to_return = order_rows_from_df(
            self.indexclass_obj.df, STORY_ID_COL_NAME, self.type2_summ_ids, NUM_MAX_RESULT_FETCH
        )

    def _do_type1_filtering(self, no_title=False):
        if no_title:
            # filter only based on special tokens
            self.df_to_return = self._get_special_token_filtered_dataframe()
        else:
            # filter based on title ids and then special tokens
            dftemp = order_rows_from_df(self.indexclass_obj.df, STORY_ID_COL_NAME, self.type1_title_ids)
            df_special_token_filtered = self._get_special_token_filtered_dataframe(dftemp)

            self.df_to_return = df_special_token_filtered

    def _get_special_token_filtered_dataframe(self, df_to_use=None):
        """
        all special token filter + appends happen here, can be added more in the future
        TODO: Filter for story "Complete" status also
        """

        if df_to_use is None:
            df_to_use = self.indexclass_obj.df

        dftemp, dftemp2 = None, None
        if self.type1_author_names:
            dftemp = order_rows_from_df(df_to_use, AUTHOR_COL_NAME, self.type1_author_names)
        if self.type1_length_name:
            dftemp2 = order_rows_from_df(df_to_use, LENGTH_COL_NAME, self.type1_length_name)
        df_combined_to_return = make_continous_appends_for_df([dftemp, dftemp2])

        return df_combined_to_return

    def get_df_result_as_dict(self):
        """return the result df"""

        return self.df_to_return.to_dict("records")