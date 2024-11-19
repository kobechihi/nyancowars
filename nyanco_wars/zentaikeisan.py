import streamlit as st

import pandas as pd

from itertools import permutations

def calculate_debuff(kill_count, original_power, disadvantage, advantage, special_character):

    original_level = 200  # 固定レベル

    level_decrease = kill_count * original_level * 0.0024

    debuff_power = original_power * (original_level - level_decrease) / original_level

    if disadvantage:

        debuff_power *= 1.25  # 不利属性の補正

    if advantage:

        debuff_power *= 0.75  # 有利属性の補正

    if special_character:

        debuff_power *= 1.13  # 複数体強化キャラor特定のキャラの補正

    return debuff_power

def calculate_kill_count(original_power, debuff_power, disadvantage, advantage, special_character):

    if original_power <= 0:

        return -1  # 元の戦力が0またはマイナスの場合は到達不可能

    kills = 0

    while True:

        current_debuff_power = calculate_debuff(kills, original_power, disadvantage, advantage, special_character)

        if current_debuff_power <= debuff_power:

            return kills

        kills += 1

        if kills > 460:  # 無限ループ防止

            return -1  # 到達不可能とする

def calculate_defense_time(location, teams):

    time_per_team = {

        "にゃんタウン": 4,

        "寮": 3,

        "城": 2

    }

    total_seconds = teams * time_per_team[location]

    minutes = total_seconds // 60

    seconds = total_seconds % 60

    return minutes, seconds

def is_disadvantage(attacker_attr, defender_attr):

    advantages = {

        "火": "木",

        "水": "火",

        "木": "水"

    }

    attacker_main = attacker_attr.split("&")[0]

    defender_main = defender_attr.split("&")[0]

    return advantages.get(attacker_main) == defender_main

def is_advantage(attacker_attr, defender_attr):

    advantages = {

        "火": "木",

        "水": "火",

        "木": "水"

    }

    attacker_main = attacker_attr.split("&")[0]

    defender_main = defender_attr.split("&")[0]

    return advantages.get(defender_main) == attacker_main

def is_special_character(attr):

    return "&" in attr

def calculate_optimal_matches(my_team_df, opponent_team_df):

    """

    Calculate the optimal matching between teams to minimize total debuff count

    """

    if len(my_team_df) == 0 or len(opponent_team_df) == 0:

        return None, None

    # インデックスをリセットして0からの連番にする

    my_team_df = my_team_df.reset_index(drop=True)

    opponent_team_df = opponent_team_df.reset_index(drop=True)

    all_my_members = list(range(len(my_team_df)))

    all_opponents = list(range(len(opponent_team_df)))

    min_total_debuff = float('inf')

    best_matches = None

    n_matches = min(len(all_my_members), len(all_opponents))

    for my_perm in permutations(all_my_members, n_matches):

        for opp_perm in permutations(all_opponents, n_matches):

            total_debuff = 0

            current_matches = []

            for i in range(n_matches):

                my_idx = my_perm[i]

                opp_idx = opp_perm[i]

                ally = my_team_df.loc[my_idx]

                opponent = opponent_team_df.loc[opp_idx]

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

def main():

    st.title("にゃんこウォーズ計算ツール")

    st.header("戦力計算[班]")

    kill_count = st.number_input("デバフ数を入力してください:", min_value=0, step=1, key="kill_count")

    original_power = st.number_input("元の戦力を入力してください[万]:", min_value=0.0, step=0.1, key="original_power")

    disadvantage = st.checkbox("属性不利ですか？", key="disadvantage")

    advantage = st.checkbox("属性有利ですか？", key="advantage")

    special_character = st.checkbox("複数体(500万以上 SSR武器 特定のキャラですか？", key="special_character")

    if st.button("戦力計算"):

        debuff_power = calculate_debuff(kill_count, original_power, disadvantage, advantage, special_character)

        st.write(f"デバフ戦力: {debuff_power:.2f}")

    st.header("防衛時間計算")

    location = st.selectbox("場所を選択してください:", ["にゃんタウン", "寮", "城"])

    teams = st.number_input("班数を入力してください:", min_value=1, step=1, key="defense_teams")

    if st.button("防衛時間計算"):

        minutes, seconds = calculate_defense_time(location, teams)

        st.write(f"防衛時間: {minutes}分 {seconds}秒")

    if 'my_team' not in st.session_state:

        st.session_state.my_team = pd.DataFrame(columns=['名前', '最高戦力', '属性'])

    if 'opponent_team' not in st.session_state:

        st.session_state.opponent_team = pd.DataFrame(columns=['名前', '最高戦力', '属性'])

    attributes = ["火", "水", "木", "火&他", "水&他", "木&他"]

    st.header("ギルドメンバー登録")

    with st.form(key='my_team_form'):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input("名前", key="my_name")

            max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="my_power")

        with col2:

            attribute = st.selectbox("属性", attributes, key="my_attribute")

        submit_button = st.form_submit_button(label='登録')

    if submit_button:

        new_data = pd.DataFrame({

            '名前': [name],

            '最高戦力': [max_power],

            '属性': [attribute],

        })

        st.session_state.my_team = pd.concat([st.session_state.my_team, new_data], ignore_index=True)

    st.header("対戦相手ギルドメンバー登録")

    with st.form(key='opponent_team_form'):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input("名前", key="opp_name")

            max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="opp_power")

        with col2:

            attribute = st.selectbox("属性", attributes, key="opp_attribute")

        submit_button = st.form_submit_button(label='登録')

    if submit_button:

        new_data = pd.DataFrame({

            '名前': [name],

            '最高戦力': [max_power],

            '属性': [attribute],

        })

        st.session_state.opponent_team = pd.concat([st.session_state.opponent_team, new_data], ignore_index=True)

    st.subheader("ギルドメンバー")

    st.dataframe(st.session_state.my_team)

    st.subheader("対戦相手ギルドメンバー")

    st.dataframe(st.session_state.opponent_team)

    if not st.session_state.my_team.empty and not st.session_state.opponent_team.empty:

        st.header("デバフ数計算結果")

        results = []

        for _, opponent in st.session_state.opponent_team.iterrows():

            for _, ally in st.session_state.my_team.iterrows():

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

                results.append({

                    '対戦相手': opponent['名前'],

                    '対戦相手戦力': opponent['最高戦力'],

                    'ギルメン': ally['名前'],

                    'デバフ数': kills_needed

                })

        results_df = pd.DataFrame(results)

        st.dataframe(results_df)

        st.header("最適な戦略提案")

        # 対戦相手の選択機能を追加

        selected_opponents = st.multiselect(

            "戦略を計算したい対戦相手を選択してください:",

            options=st.session_state.opponent_team['名前'].tolist()

        )

        if st.button("最適な組み合わせを計算"):

            if selected_opponents:

                # 選択された対戦相手のデータフレームを作成

                selected_opponent_df = st.session_state.opponent_team[

                    st.session_state.opponent_team['名前'].isin(selected_opponents)

                ]

                best_matches, total_debuff = calculate_optimal_matches(

                    st.session_state.my_team,

                    selected_opponent_df

                )

                if best_matches:

                    st.write(f"最小合計デバフ数: {total_debuff}")

                    st.write("推奨される組み合わせ:")

                    best_matches_df = pd.DataFrame(best_matches)

                    st.dataframe(best_matches_df)

                else:

                    st.write("有効な組み合わせが見つかりませんでした。")

            else:

                st.write("対戦相手を選択してください。")

if __name__ == "__main__":

    main() 
