import streamlit as st

import pandas as pd

import itertools

# 既存の関数はすべてそのままにします

def find_best_strategy(results_df):

    best_combination = None

    min_total_debuffs = float('inf')

    # ギルドメンバーの名前をリスト化

    members = results_df['ギルメン'].unique()

    # ギルメンの組み合わせを生成

    for combination in itertools.product(members, repeat=2):

        total_debuffs = results_df.loc[

            (results_df['ギルメン'].isin(combination)) & 

            (results_df['対戦相手'].isin(results_df['対戦相手']))

        ]['デバフ数'].sum()

        if total_debuffs < min_total_debuffs:

            min_total_debuffs = total_debuffs

            best_combination = combination

    return best_combination, min_total_debuffs

def main():

    st.title("にゃんこウォーズ計算ツール")

    # 既存のUIはそのままにします

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

        # 戦略提案の表示

        if not results_df.empty:

            best_combination, min_total_debuffs = find_best_strategy(results_df)

            st.header("戦略提案")

            st.write(f"最適なギルメンの組み合わせ: {best_combination[0]} と {best_combination[1]}")

            st.write(f"合計デバフ数: {min_total_debuffs}")

if __name__ == "__main__":

    main()
 
