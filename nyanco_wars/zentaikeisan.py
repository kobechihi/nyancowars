import streamlit as st

import pandas as pd

import itertools

def calculate_debuff(kill_count, original_power, disadvantage, advantage, special_character, high_power):

    original_level = 200  # 固定レベル

    level_decrease = kill_count * original_level * 0.0024

    debuff_power = original_power * (original_level - level_decrease) / original_level

    if disadvantage:

        debuff_power *= 1.25  # 不利属性の補正

    if advantage:

        debuff_power *= 0.75  # 有利属性の補正

    if special_character:

        debuff_power *= 1.13  # 複数体強化キャラor特定のキャラの補正

    if high_power:

        debuff_power = calculate_debuff(kill_count - 30, original_power, disadvantage, advantage, special_character, False)

    return debuff_power

def calculate_kill_count(original_power, debuff_power, disadvantage, advantage, special_character):

    if original_power <= 0:

        return -1  # 元の戦力が0またはマイナスの場合は到達不可能

    kills = 0

    while True:

        current_debuff_power = calculate_debuff(kills, original_power, disadvantage, advantage, special_character, False)

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

def main():

    st.title("にゃんこウォーズ計算ツール")

    st.header("戦力計算[班]")

    kill_count = st.number_input("デバフ数を入力してください:", min_value=0, step=1, key="kill_count")

    original_power = st.number_input("元の戦力を入力してください[万]:", min_value=0.0, step=0.1, key="original_power")

    disadvantage = st.checkbox("属性不利ですか？", key="disadvantage")

    advantage = st.checkbox("属性有利ですか？", key="advantage")

    special_character = st.checkbox("複数体(500万以上) SSR武器 特定のキャラですか？", key="special_character")

    high_power = st.checkbox("戦力3000万以上ですか？", key="high_power")

    if st.button("戦力計算"):

        debuff_power = calculate_debuff(kill_count, original_power, disadvantage, advantage, special_character, high_power)

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

    st.markdown("3000万以上の相手には名前の後ろに#をつけてください", unsafe_allow_html=True)

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

        # 戦略提案機能

        st.header("戦略提案")

        # ギルドメンバーの出撃回数を制限する

        opponent_names = st.session_state.opponent_team['名前'].tolist()

        ally_names = st.session_state.my_team['名前'].tolist()

        # ギルドメンバーの出撃回数制限

        max_deploy_count = 2

        ally_count = len(opponent_names) * 2  # 各対戦相手に対して2回出撃

        possible_allies = [ally for ally in ally_names for _ in range(max_deploy_count)]

        best_strategy = None

        min_total_debuff = float('inf')

        # 可能な組み合わせを生成する際に、出撃回数を考慮する

        for ally_combo in itertools.combinations_with_replacement(possible_allies, ally_count):

            if all(ally_combo.count(ally) <= max_deploy_count for ally in set(ally_combo)):

                current_strategy = list(zip(opponent_names * 2, ally_combo))

                total_debuff = sum(

                    results_df[(results_df['対戦相手'] == opp) & (results_df['ギルメン'] == ally)]['デバフ数'].iloc[0]

                    for opp, ally in current_strategy

                    if not results_df[(results_df['対戦相手'] == opp) & (results_df['ギルメン'] == ally)].empty

                )

                if total_debuff < min_total_debuff:

                    min_total_debuff = total_debuff

                    best_strategy = current_strategy

        if best_strategy:

            st.subheader("最適な戦略:")

            for opp, ally in best_strategy:

                debuff = results_df[(results_df['対戦相手'] == opp) & (results_df['ギルメン'] == ally)]['デバフ数'].iloc[0]

                st.write(f"{opp}は{ally}（デバフ数 {debuff}）")

            st.write(f"合計デバフ数は{min_total_debuff}")

        else:

            st.write("戦略を計算できませんでした。データを確認してください。")

if __name__ == "__main__":

    main()
 
