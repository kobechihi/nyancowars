import streamlit as st

import pandas as pd

import numpy as np

def calculate_debuff(kill_count, original_level, original_power, disadvantage):

    level_decrease = kill_count * original_level * 0.0024

    debuff_power = original_power * (original_level - level_decrease) / original_level

    if disadvantage:

        debuff_power *= 0.8

    return debuff_power

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

def calculate_required_kills(ally_power, opponent_power, ally_attribute, opponent_attribute):

    disadvantage = (ally_attribute == "火" and opponent_attribute == "水") or \

                   (ally_attribute == "水" and opponent_attribute == "木") or \

                   (ally_attribute == "木" and opponent_attribute == "火")

    advantage = (ally_attribute == "水" and opponent_attribute == "火") or \

                (ally_attribute == "木" and opponent_attribute == "水") or \

                (ally_attribute == "火" and opponent_attribute == "木")

    if disadvantage:

        ally_power *= 0.8

    elif advantage:

        opponent_power *= 0.8

    if ally_power >= opponent_power:

        return 0

    # 繰り返し計算の最適化

    kill_count = 0

    while ally_power * (1 - kill_count * 0.0024) < opponent_power:

        kill_count += 1

    return kill_count

def main():

    st.title("にゃんこウォーズ計算ツール")

    # セッションステートの初期化

    if 'my_team' not in st.session_state:

        st.session_state.my_team = []

    if 'opponent_team' not in st.session_state:

        st.session_state.opponent_team = []

    # 自チームメンバー登録フォーム

    st.header("自チームメンバー登録")

    with st.form(key='my_team_form'):

        name = st.text_input("名前", key="my_name")

        max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="my_power")

        attribute = st.selectbox("属性", ["火", "水", "木"], key="my_attribute")

        level = st.number_input("レベル", min_value=1, max_value=200, value=200, step=1, key="my_level")

        submit_button = st.form_submit_button(label='自チームに登録')

    if submit_button:

        st.session_state.my_team.append({

            '名前': name,

            '最高戦力': f"{max_power}万",

            '属性': attribute,

            'レベル': level

        })

    # 対戦相手チームメンバー登録フォーム

    st.header("対戦相手チームメンバー登録")

    with st.form(key='opponent_team_form'):

        guild_name = st.text_input("ギルド名", key="opp_guild")

        name = st.text_input("名前", key="opp_name")

        max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="opp_power")

        attribute = st.selectbox("属性", ["火", "水", "木"], key="opp_attribute")

        submit_button = st.form_submit_button(label='対戦相手チームに登録')

    if submit_button:

        st.session_state.opponent_team.append({

            'ギルド名': guild_name,

            '名前': name,

            '最高戦力': f"{max_power}万",

            '属性': attribute

        })

    # 自チームと対戦相手チームのデータ表示

    st.subheader("自チームメンバー")

    st.write(st.session_state.my_team)

    st.subheader("対戦相手チームメンバー")

    st.write(st.session_state.opponent_team)

    # デバフ逆算

    if st.session_state.my_team and st.session_state.opponent_team:

        st.header("デバフ逆算")

        for opponent in st.session_state.opponent_team:

            st.subheader(f"対戦相手: {opponent['名前']} (戦力: {opponent['最高戦力']}, 属性: {opponent['属性']})")

            opponent_power = float(opponent['最高戦力'].rstrip('万'))

            results = []

            for ally in st.session_state.my_team:

                ally_power = float(ally['最高戦力'].rstrip('万'))

                required_kills = calculate_required_kills(ally_power, opponent_power, ally['属性'], opponent['属性'])

                results.append({

                    '名前': ally['名前'],

                    '戦力': ally['最高戦力'],

                    '属性': ally['属性'],

                    '必要KILL数': required_kills

                })

            # 必要KILL数が少ない順に並べ替え

            results.sort(key=lambda x: x['必要KILL数'])

            top_results = results[:3]  # 上位3名を表示

            st.write("攻撃メンバー（必要KILL数順）：")

            for row in top_results:

                st.write(f"  {row['名前']} (戦力: {row['戦力']}, 属性: {row['属性']}) - 必要KILL数: {row['必要KILL数']}")

    # 防衛時間計算

    st.header("防衛時間計算")

    location = st.selectbox("場所を選択してください:", ["にゃんタウン", "寮", "城"])

    teams = st.number_input("班数を入力してください:", min_value=1, step=1, key="defense_teams")

    if st.button("防衛時間計算"):

        minutes, seconds = calculate_defense_time(location, teams)

        st.write(f"防衛時間: {minutes}分 {seconds}秒")

if __name__ == "__main__":

    main()
 
