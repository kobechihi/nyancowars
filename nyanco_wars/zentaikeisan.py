import streamlit as st

import pandas as pd

import numpy as np

def calculate_debuff(kill_count, original_level, original_power, disadvantage, kakin):

    level_decrease = kill_count * original_level * 0.0024

    debuff_power = original_power * (original_level - level_decrease) / original_level

    if disadvantage:

        debuff_power *= 1.25

    if kakin:

        debuff_power *= 1.125

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

def calculate_required_kills(ally_power, opponent_power, ally_level, disadvantage, ally_kakin, opponent_kakin):

    target_power = opponent_power

    if disadvantage:

        target_power *= 1.25

    if ally_kakin:

        target_power /= 1.125

    if opponent_kakin:

        target_power *= 1.125

    if ally_power >= target_power:

        return 0

    required_debuff = (target_power - ally_power) / ally_power

    required_kills = int(required_debuff / (0.0024 * ally_level)) + 1

    return required_kills

def main():

    st.title("にゃんこウォーズ計算ツール")

    # デバフ計算（戦力計算）

    st.header("戦力計算")

    kill_count = st.number_input("KILL数を入力してください:", min_value=0, step=1, key="kill_count")

    original_level = st.number_input("もとのレベルを入力してください[戦力400万以上なら200が目安]:", min_value=0.0, step=0.1, key="original_level")

    original_power = st.number_input("元の戦力を入力してください[万]:", min_value=0.0, step=0.1, key="original_power")

    disadvantage = st.checkbox("不利属性ですか？", key="disadvantage")

    kakin = st.checkbox("魔石・装備のレベルは高いですか？", key="kakin")

    if st.button("戦力計算"):

        level_decrease, debuff_power = calculate_debuff(kill_count, original_level, original_power, disadvantage, kakin)

        st.write(f"デバフ戦力: {debuff_power:.2f}万")

    # 防衛時間計算

    st.header("防衛時間計算")

    location = st.selectbox("場所を選択してください:", ["にゃんタウン", "寮", "城"])

    teams = st.number_input("班数を入力してください:", min_value=1, step=1, key="defense_teams")

    if st.button("防衛時間計算"):

        minutes, seconds = calculate_defense_time(location, teams)

        st.write(f"防衛時間: {minutes}分 {seconds}秒")

    # セッションステートの初期化

    if 'my_team' not in st.session_state:

        st.session_state.my_team = pd.DataFrame(columns=['名前', '最高戦力', '属性', '課金', 'レベル'])

    if 'opponent_team' not in st.session_state:

        st.session_state.opponent_team = pd.DataFrame(columns=['ギルド名', '名前', '最高戦力', '属性', '課金'])

    # ギルドメンバー登録フォーム

    st.header("ギルドメンバー登録")

    with st.form(key='my_team_form'):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input("名前", key="my_name")

            max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="my_power")

            level = st.number_input("レベル", min_value=1, max_value=200, value=200, step=1, key="my_level")

        with col2:

            attribute = st.selectbox("属性", ["火", "水", "木"], key="my_attribute")

            kakin = st.checkbox("課金プレイヤーですか？", key="my_kakin")

        submit_button = st.form_submit_button(label='自チームに登録')

    if submit_button:

        new_data = pd.DataFrame({

            '名前': [name],

            '最高戦力': [f"{max_power}万"],

            '属性': [attribute],

            '課金': [kakin],

            'レベル': [level]

        })

        st.session_state.my_team = pd.concat([st.session_state.my_team, new_data], ignore_index=True)

    # 対戦相手チームメンバー登録フォーム

    st.header("対戦相手チームメンバー登録")

    with st.form(key='opponent_team_form'):

        col1, col2 = st.columns(2)

        with col1:

            guild_name = st.text_input("ギルド名", key="opp_guild")

            name = st.text_input("名前", key="opp_name")

            max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="opp_power")

        with col2:

            attribute = st.selectbox("属性", ["火", "水", "木"], key="opp_attribute")

            kakin = st.checkbox("課金プレイヤーですか？", key="opp_kakin")

        submit_button = st.form_submit_button(label='対戦相手チームに登録')

    if submit_button:

        new_data = pd.DataFrame({

            'ギルド名': [guild_name],

            '名前': [name],

            '最高戦力': [f"{max_power}万"],

            '属性': [attribute],

            '課金': [kakin]

        })

        st.session_state.opponent_team = pd.concat([st.session_state.opponent_team, new_data], ignore_index=True)

    # データの表示

    st.subheader("自チームメンバー")

    st.dataframe(st.session_state.my_team)

    st.subheader("対戦相手チームメンバー")

    st.dataframe(st.session_state.opponent_team)

    # デバフ逆算

    if not st.session_state.my_team.empty and not st.session_state.opponent_team.empty:

        st.header("デバフ逆算")

        for _, opponent in st.session_state.opponent_team.iterrows():

            st.subheader(f"対戦相手: {opponent['名前']} (戦力: {opponent['最高戦力']})")

            opponent_power = float(opponent['最高戦力'].rstrip('万'))

            results = []

            for _, ally in st.session_state.my_team.iterrows():

                ally_power = float(ally['最高戦力'].rstrip('万'))

                ally_level = ally['レベル']

                disadvantage = (ally['属性'] == "火" and opponent['属性'] == "水") or \
                               (ally['属性'] == "水" and opponent['属性'] == "木") or \
                               (ally['属性'] == "木" and opponent['属性'] == "火")

                required_kills = calculate_required_kills(ally_power, opponent_power, ally_level, disadvantage, ally['課金'], opponent['課金'])

                results.append({

                    '名前': ally['名前'],

                    '戦力': ally['最高戦力'],

                    '必要KILL数': required_kills

                })

            # 必要KILL数が少ない順に並べ替えて上位3名を表示

            results_df = pd.DataFrame(results)

            results_df = results_df.sort_values('必要KILL数')

            top_3 = results_df.head(3)

            st.write("推奨攻撃メンバー（必要KILL数が少ない順）：")

            for _, row in top_3.iterrows():

                st.write(f"  {row['名前']} (戦力: {row['戦力']}) - 必要KILL数: {row['必要KILL数']}")

if __name__ == "__main__":

    main()
 
