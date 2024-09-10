import streamlit as st

import pandas as pd

def calculate_debuff(kill_count, original_level, original_power, disadvantage, kakin):

    level_decrease = kill_count * original_level * 0.0024

    debuff_power = original_power * (original_level - level_decrease) / original_level

    if disadvantage:

        debuff_power *= 1.25

    if kakin:

        debuff_power *= 1.13

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

def main():

    st.title("にゃんこウォーズ計算ツール")

    # デバフ計算（戦力計算）

    st.header("戦力計算[班]")

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

        st.session_state.my_team = pd.DataFrame(columns=['ギルド名', '名前', '最高戦力', '属性', '課金'])

    if 'opponent_team' not in st.session_state:

        st.session_state.opponent_team = pd.DataFrame(columns=['ギルド名', '名前', '最高戦力', '属性', '課金'])

    # ギルドメンバー登録フォーム

    st.header("ギルドメンバー登録")

    with st.form(key='my_team_form'):

        col1, col2 = st.columns(2)

        with col1:

            guild_name = st.text_input("ギルド名", key="my_guild")

            name = st.text_input("名前", key="my_name")

            max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="my_power")

        with col2:

            attribute = st.selectbox("属性", ["火", "水", "木"], key="my_attribute")

            kakin = st.checkbox("課金プレイヤーですか？", key="my_kakin")

        submit_button = st.form_submit_button(label='自チームに登録')

    if submit_button:

        new_data = pd.DataFrame({

            'ギルド名': [guild_name],

            '名前': [name],

            '最高戦力': [f"{max_power}万"],

            '属性': [attribute],

            '課金': [kakin]

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

    # デバフ計算と勝利可能メンバーの表示

    if not st.session_state.my_team.empty and not st.session_state.opponent_team.empty:

        st.header("デバフ逆算")

        for _, opponent in st.session_state.opponent_team.iterrows():

            st.subheader(f"対戦相手: {opponent['名前']} (戦力: {opponent['最高戦力']})")

            for _, ally in st.session_state.my_team.iterrows():

                original_power = float(ally['最高戦力'].rstrip('万'))

                opponent_power = float(opponent['最高戦力'].rstrip('万'))

                required_debuff = max(0, (opponent_power - original_power) / opponent_power)

                required_kills = int(required_debuff / (0.0024 * 200))  # Assuming level 200 for simplicity

                st.write(f"{ally['名前']} (戦力: {ally['最高戦力']}):")

                if original_power > opponent_power:

                    st.write(f"  勝利可能！ デバフ不要")

                else:

                    st.write(f"  必要なデバフ: {required_debuff:.2%}")

                    st.write(f"  必要なKILL数(概算): {required_kills}")

                # 課金状況による補正

                if ally['課金'] and not opponent['課金']:

                    st.write("  課金による有利: 必要なKILL数が少なくなる可能性があります")

                elif not ally['課金'] and opponent['課金']:

                    st.write("  課金による不利: 必要なKILL数が多くなる可能性があります")

if __name__ == "__main__":

    main()
 
