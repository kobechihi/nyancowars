import streamlit as st

import pandas as pd

from itertools import permutations

# [Previous code remains exactly the same until the last part]

# Add this new function before the main() function:

def calculate_optimal_matches(my_team_df, opponent_team_df):

    """

    Calculate the optimal matching between teams to minimize total debuff count

    """

    if len(my_team_df) == 0 or len(opponent_team_df) == 0:

        return None

    all_my_members = my_team_df.index.tolist()

    all_opponents = opponent_team_df.index.tolist()

    # Get all possible permutations of matches

    min_total_debuff = float('inf')

    best_matches = None

    # Use the shorter team's length to determine the number of matches

    n_matches = min(len(all_my_members), len(all_opponents))

    for my_perm in permutations(all_my_members, n_matches):

        for opp_perm in permutations(all_opponents, n_matches):

            total_debuff = 0

            current_matches = []

            for i in range(n_matches):

                my_idx = my_perm[i]

                opp_idx = opp_perm[i]

                ally = my_team_df.iloc[my_idx]

                opponent = opponent_team_df.iloc[opp_idx]

                disadvantage = is_disadvantage(opponent['属性'], ally['属性'])

                advantage = is_advantage(opponent['属性'], ally['属性'])

                special_character = is_special_character(opponent['属性'])

                kills_needed = calculate_kill_count(

                    opponent['最高戦力'], 

                    ally['最高戦力'], 

                    disadvantage, 

                    advantage, 

                    special_character

                )

                # Add 30 to kills_needed if opponent name contains '#'

                if '#' in opponent['名前']:

                    kills_needed += 30

                if kills_needed == -1:  # Skip impossible combinations

                    total_debuff = float('inf')

                    break

                total_debuff += kills_needed

                current_matches.append({

                    '対戦相手': opponent['名前'],

                    '対戦相手戦力': opponent['最高戦力'],

                    'ギルメン': ally['名前'],

                    'デバフ数': kills_needed

                })

            if total_debuff < min_total_debuff:

                min_total_debuff = total_debuff

                best_matches = current_matches

    return best_matches, min_total_debuff

# Modify the end of the main() function, after the results_df display:

    if not st.session_state.my_team.empty and not st.session_state.opponent_team.empty:

        st.header("デバフ数計算結果")

        results = []

        for _, opponent in st.session_state.opponent_team.iterrows():

            for _, ally in st.session_state.my_team.iterrows():

                disadvantage = is_disadvantage(opponent['属性'], ally['属性'])

                advantage = is_advantage(opponent['属性'], ally['属性'])

                special_character = is_special_character(opponent['属性'])

                kills_needed = calculate_kill_count(opponent['最高戦力'], ally['最高戦力'], disadvantage, advantage, special_character)

                if '#' in opponent['名前']:

                    kills_needed += 30

                results.append({

                    '対戦相手': opponent['名前'],

                    '対戦相手戦力': opponent['最高戦力'],

                    'ギルメン': ally['名前'],

                    'デバフ数': kills_needed

                })

        results_df = pd.DataFrame(results)

        st.dataframe(results_df)

        # Add strategy suggestion section

        st.header("最適な戦略提案")

        if st.button("最適な組み合わせを計算"):

            best_matches, total_debuff = calculate_optimal_matches(

                st.session_state.my_team,

                st.session_state.opponent_team

            )

            if best_matches:

                st.write(f"最小合計デバフ数: {total_debuff}")

                st.write("推奨される組み合わせ:")

                best_matches_df = pd.DataFrame(best_matches)

                st.dataframe(best_matches_df)

            else:

                st.write("有効な組み合わせが見つかりませんでした。")

if __name__ == "__main__":

    main() 
