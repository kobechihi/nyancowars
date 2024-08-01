import streamlit as st
import pandas as pd

def calculate_debuff(kill_count, original_level, original_power, disadvantage, kakin):

    level_decrease = kill_count * original_level * 0.0024

    debuff_power = original_power * (original_level - level_decrease) / original_level

    if disadvantage:

        debuff_power *= 1.25

    if kakin:

        debuff_power *= 1.1

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


        st.write(f"デバフ戦力: {debuff_power:.2f}")

    # 防衛時間計算

    st.header("防衛時間計算")

    location = st.selectbox("場所を選択してください:", ["にゃんタウン", "寮", "城"])

    teams = st.number_input("班数を入力してください:", min_value=1, step=1, key="defense_teams")

    if st.button("防衛時間計算"):

        minutes, seconds = calculate_defense_time(location, teams)

        st.write(f"防衛時間: {minutes}分 {seconds}秒")

    # セッションステートの初期化

    if 'data' not in st.session_state:

        st.session_state.data = pd.DataFrame(columns=['ギルド名', '名前', '最高戦力', '属性', '班数'])

    # ギルドメンバー登録フォーム

    st.header("ギルドメンバー登録")

    with st.form(key='data_form'):

        col1, col2 = st.columns(2)

        with col1:

            guild_name = st.text_input("ギルド名")

            name = st.text_input("名前")

            max_power = st.number_input("最高戦力", min_value=0.0, step=0.1)

        with col2:

            attribute = st.selectbox("属性", ["火", "水", "木"])

            team_count = st.number_input("班数", min_value=1, step=1)

        submit_button = st.form_submit_button(label='登録')

    if submit_button:

        new_data = pd.DataFrame({

            'ギルド名': [guild_name],

            '名前': [name],

            '最高戦力': [max_power],

            '属性': [attribute],

            '班数': [team_count]

        })

        st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)

    # データの表示

    st.subheader("登録されたメンバー")

    st.dataframe(st.session_state.data)

if __name__ == "__main__":

    main()
 
