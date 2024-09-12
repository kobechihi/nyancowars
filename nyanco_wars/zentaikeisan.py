import streamlit as st

import pandas as pd

import numpy as np

def calculate_debuff(kill_count, original_level, original_power, disadvantage):

    level_decrease = kill_count * original_level * 0.0024

    debuff_power = original_power * (original_level - level_decrease) / original_level

    if disadvantage:

        debuff_power *= 1.25

    return level_decrease, debuff_power

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

def calculate_required_kills(original_power, target_power, original_level, disadvantage):

    def objective(kill_count):

        _, debuff_power = calculate_debuff(kill_count, original_level, original_power, disadvantage)

        return debuff_power - target_power

    # 二分探索法でKILL数を見つける

    low, high = 0, 1000

    while high - low > 1:

        mid = (low + high) // 2

        if objective(mid) > 0:

            low = mid

        else:

            high = mid

    return high

def main():

    st.title("にゃんこウォーズ計算ツール")

    # デバフ計算（戦力計算）

    st.header("戦力計算[班]")

    kill_count = st.number_input("KILL数を入力してください:", min_value=0, step=1, key="kill_count")

    original_level = st.number_input("もとのレベルを入力してください[戦力400万以上なら200が目安]:", min_value=0.0, step=0.1, key="original_level")

    original_power = st.number_input("元の戦力を入力してください[万]:", min_value=0.0, step=0.1, key="original_power")

    disadvantage = st.checkbox("不利属性ですか？", key="disadvantage")

    if st.button("戦力計算"):

        level_decrease, debuff_power = calculate_debuff(kill_count, original_level, original_power, disadvantage)

        st.write(f"デバフ戦力: {debuff_power:.2f}")

    # 防衛時間計算

    st.header("防衛時間計算")

    location = st.selectbox("場所を選択してください:", ["にゃんタウン", "寮", "城"])

    teams = st.number_input("班数を入力してください:", min_value=1, step=1, key="defense_teams")

    if st.button("防衛時間計算"):

        minutes, seconds = calculate_defense_time(location, teams)

        st.write(f"防衛時間: {minutes}分 {seconds}秒")

    # セッションステートの初期化

    if 'my_team' not in st.session_state:

        st.session_state.my_team = pd.DataFrame(columns=['名前', '最高戦力', '属性'])

    if 'opponent_team' not in st.session_state:

        st.session_state.opponent_team = pd.DataFrame(columns=['ギルド名', '名前', '最高戦力', '属性'])

    # 自チームメンバー登録フォーム

    st.header("自チームメンバー登録")

    with st.form(key='my_team_form'):

        name = st.text_input("名前", key="my_name")

        max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="my_power")

        attribute = st.selectbox("属性", ["火", "水", "木"], key="my_attribute")

        submit_button = st.form_submit_button(label='自チームに登録')

    if submit_button:

        new_data = pd.DataFrame({

            '名前': [name],

            '最高戦力': [max_power],

            '属性': [attribute]

        })

        st.session_state.my_team = pd.concat([st.session_state.my_team, new_data], ignore_index=True)

    # 対戦相手チームメンバー登録フォーム

    st.header("対戦相手チームメンバー登録")

    with st.form(key='opponent_team_form'):

        guild_name = st.text_input("ギルド名", key="opp_guild")

        name = st.text_input("名前", key="opp_name")

        max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="opp_power")

        attribute = st.selectbox("属性", ["火", "水", "木"], key="opp_attribute")

        submit_button = st.form_submit_button(label='対戦相手チームに登録')

    if submit_button:

        new_data = pd.DataFrame({

            'ギルド名': [guild_name],

            '名前': [name],

            '最高戦力': [max_power],

            '属性': [attribute]

        })

        st.session_state.opponent_team = pd.concat([st.session_state.opponent_team, new_data], ignore_index=True)

    # データの表示

    st.subheader("自チームメンバー")

    st.dataframe(st.session_state.my_team)

    st.subheader("対戦相手チームメンバー")

    st.dataframe(st.session_state.opponent_team)

    # デバフ逆算機能

    st.header("デバフ逆算")

    if 'my_team' in st.session_state and 'opponent_team' in st.session_state:

        if not st.session_state.my_team.empty and not st.session_state.opponent_team.empty:

            st.write("自チームメンバーが敵対チームメンバーの戦力と同じになるKILL数を計算します。")

            for _, my_member in st.session_state.my_team.iterrows():

                st.subheader(f"{my_member['名前']}のデバフ逆算")

                for _, opp_member in st.session_state.opponent_team.iterrows():

                    original_power = my_member['最高戦力']

                    target_power = opp_member['最高戦力']

                    original_level = st.number_input(f"{my_member['名前']}のもとのレベル[戦力400万以上なら200が目安]:", 

                                                     min_value=0.0, step=0.1, key=f"level_{my_member['名前']}_{opp_member['名前']}")

                    disadvantage = st.checkbox(f"{my_member['名前']}が{opp_member['名前']}に対して不利属性ですか？", 

                                               key=f"disadvantage_{my_member['名前']}_{opp_member['名前']}")

                    required_kills = calculate_required_kills(original_power, target_power, original_level, disadvantage)

                    st.write(f"{my_member['名前']}が{opp_member['名前']}(戦力: {target_power})と同じ戦力になるために必要なKILL数: {required_kills}")

        else:

            st.write("自チームメンバーと敵対チームメンバーを登録してください。")

    else:

        st.write("自チームメンバーと敵対チームメンバーを登録してください。")

if __name__ == "__main__":

    main()
 
