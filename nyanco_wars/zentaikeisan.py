import streamlit as st

import pandas as pd

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

        if kills > 1000:  # 無限ループ防止

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

        "木": "水",

        "火複数": "木",

        "水複数": "火",

        "木複数": "水"

    }

    return advantages.get(attacker_attr) == defender_attr

def is_advantage(attacker_attr, defender_attr):

    advantages = {

        "火": "木",

        "水": "火",

        "木": "水",

        "火複数": "木",

        "水複数": "火",

        "木複数": "水"

    }

    return advantages.get(defender_attr) == attacker_attr.replace("複数", "")

def is_special_character(attr):

    return "複数" in attr

def main():

    st.title("にゃんこウォーズ計算ツール")

    st.header("戦力計算[班]")

    kill_count = st.number_input("KILL数を入力してください:", min_value=0, step=1, key="kill_count")

    original_power = st.number_input("元の戦力を入力してください[万]:", min_value=0.0, step=0.1, key="original_power")

    disadvantage = st.checkbox("属性不利ですか？", key="disadvantage")

    advantage = st.checkbox("属性有利ですか？", key="advantage")

    special_character = st.checkbox("複数体強化キャラがいるor特定のキャラですか？", key="special_character")

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

    attributes = ["火", "水", "木", "火複数", "水複数", "木複数"]

    st.header("自チームメンバー登録")

    with st.form(key='my_team_form'):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input("名前", key="my_name")

            max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="my_power")

        with col2:

            attribute = st.selectbox("属性", attributes, key="my_attribute")

        submit_button = st.form_submit_button(label='自チームに登録')

    if submit_button:

        new_data = pd.DataFrame({

            '名前': [name],

            '最高戦力': [max_power],

            '属性': [attribute],

        })

        st.session_state.my_team = pd.concat([st.session_state.my_team, new_data], ignore_index=True)

    st.header("対戦相手チームメンバー登録")

    with st.form(key='opponent_team_form'):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input("名前", key="opp_name")

            max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="opp_power")

        with col2:

            attribute = st.selectbox("属性", attributes, key="opp_attribute")

        submit_button = st.form_submit_button(label='対戦相手チームに登録')

    if submit_button:

        new_data = pd.DataFrame({

            '名前': [name],

            '最高戦力': [max_power],

            '属性': [attribute],

        })

        st.session_state.opponent_team = pd.concat([st.session_state.opponent_team, new_data], ignore_index=True)

    st.subheader("自チームメンバー")

    st.dataframe(st.session_state.my_team)

    st.subheader("対戦相手チームメンバー")

    st.dataframe(st.session_state.opponent_team)

    if not st.session_state.my_team.empty and not st.session_state.opponent_team.empty:

        st.header("必要デバフ数計算結果")

        results = []

        for _, opponent in st.session_state.opponent_team.iterrows():

            for _, ally in st.session_state.my_team.iterrows():

                disadvantage = is_disadvantage(opponent['属性'], ally['属性'])

                advantage = is_advantage(opponent['属性'], ally['属性'])

                special_character = is_special_character(opponent['属性'])

                kills_needed = calculate_kill_count(opponent['最高戦力'], ally['最高戦力'], disadvantage, advantage, special_character)

                results.append({

                    '対戦相手': opponent['名前'],

                    '自チーム': ally['名前'],

                    '必要デバフ数': kills_needed

                })

        results_df = pd.DataFrame(results)

        st.dataframe(results_df)

if __name__ == "__main__":

    main()
 
