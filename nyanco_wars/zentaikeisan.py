import streamlit as st

import pandas as pd

def calculate_debuff(kill_count, original_level, original_power, disadvantage):

    level_decrease = kill_count * original_level * 0.0024

    debuff_power = original_power * (original_level - level_decrease) / original_level

    return level_decrease, debuff_power * (0.8 if disadvantage else 1)

def calculate_required_kills(ally_power, opponent_power, ally_attribute, opponent_attribute):

    disadvantages = {"火": "水", "水": "木", "木": "火"}

    advantage = {v: k for k, v in disadvantages.items()}

    if disadvantages.get(ally_attribute) == opponent_attribute:

        ally_power *= 0.8

    elif advantage.get(ally_attribute) == opponent_attribute:

        opponent_power *= 0.8

    if ally_power >= opponent_power:

        return 0

    original_level = 200

    kill_count = 0

    current_power = ally_power

    while current_power < opponent_power:

        kill_count += 1

        _, current_power = calculate_debuff(kill_count, original_level, ally_power, False)

    return kill_count

def main():

    st.title("にゃんこウォーズ計算ツール")

    # デバフ計算

    st.header("戦力計算")

    kill_count = st.number_input("KILL数:", min_value=0, step=1)

    original_level = st.number_input("もとのレベル:", min_value=0.0, step=0.1)

    original_power = st.number_input("元の戦力:", min_value=0.0, step=0.1)

    disadvantage = st.checkbox("不利属性")

    if st.button("戦力計算"):

        level_decrease, debuff_power = calculate_debuff(kill_count, original_level, original_power, disadvantage)

        st.write(f"デバフ戦力: {debuff_power:.2f}万")

    # ギルドメンバー登録

    if 'my_team' not in st.session_state:

        st.session_state.my_team = []

    st.header("ギルドメンバー登録")

    with st.form(key='my_team_form'):

        name = st.text_input("名前")

        max_power = st.number_input("最高戦力", min_value=0.0, step=0.1)

        attribute = st.selectbox("属性", ["火", "水", "木"])

        level = st.number_input("レベル", min_value=1, max_value=200, value=200, step=1)

        submit_button = st.form_submit_button(label='登録')

    if submit_button:

        st.session_state.my_team.append({

            '名前': name, '最高戦力': f"{max_power}万", '属性': attribute, 'レベル': level

        })

    st.subheader("自チームメンバー")

    st.dataframe(pd.DataFrame(st.session_state.my_team))

if __name__ == "__main__":

    main()
 
