import streamlit as st

import pandas as pd

def calculate_debuff(kill_count, original_power, disadvantage, kakin):

    original_level = 200  # Fixed level

    level_decrease = kill_count * original_level * 0.0024

    debuff_power = original_power * (original_level - level_decrease) / original_level

    if disadvantage:

        debuff_power *= 1.25

    if kakin:

        debuff_power *= 1.15

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

def calculate_kills_needed(my_team, opponent_team):

    attribute_advantage = {

        "火": "木",  # 火は木に強い

        "水": "火",  # 水は火に強い

        "木": "水"   # 木は水に強い

    }

    kills_needed = []

    for _, opp_row in opponent_team.iterrows():

        opponent_power = opp_row['最高戦力']

        opp_attribute = opp_row['属性']

        for _, my_row in my_team.iterrows():

            my_power = my_row['最高戦力']

            my_attribute = my_row['属性']

            if my_attribute == attribute_advantage.get(opp_attribute):

                effective_power = my_power * 1.5  # 有利属性

            elif my_attribute == opp_attribute:

                effective_power = my_power  # 同属性

            else:

                effective_power = my_power * 0.5  # 不利属性

            if effective_power >= opponent_power:

                required_kills = (200 / effective_power) / 0.0024  # 逆算

            else:

                required_kills = float('inf')  # 倒せない場合

            kills_needed.append({

                '対戦相手': opp_row['名前'],

                '自チームメンバー': my_row['名前'],

                '必要KILL数': required_kills

            })

    return pd.DataFrame(kills_needed)

def main():

    st.title("にゃんこウォーズ計算ツール")

    st.header("戦力計算[班]")

    kill_count = st.number_input("KILL数を入力してください:", min_value=0, step=1, key="kill_count")

    original_power = st.number_input("元の戦力を入力してください[万]:", min_value=0.0, step=0.1, key="original_power")

    disadvantage = st.checkbox("不利属性ですか？", key="disadvantage")

    kakin = st.checkbox("魔石・装備のレベルは高いですか？", key="kakin")

    if st.button("戦力計算"):

        level_decrease, debuff_power = calculate_debuff(kill_count, original_power, disadvantage, kakin)

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

    st.header("自チームメンバー登録")

    with st.form(key='my_team_form'):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input("名前", key="my_name")

            max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="my_power")

        with col2:

            attribute = st.selectbox("属性", ["火", "水", "木"], key="my_attribute")

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

            attribute = st.selectbox("属性", ["火", "水", "木"], key="opp_attribute")

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

        st.header("必要KILL数計算")

        if st.button("計算"):

            kills_needed_df = calculate_kills_needed(st.session_state.my_team, st.session_state.opponent_team)

            st.dataframe(kills_needed_df)

if __name__ == "__main__":

    main()
 
