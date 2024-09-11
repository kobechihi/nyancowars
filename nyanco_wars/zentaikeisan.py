def main():

    st.title("にゃんこウォーズ計算ツール")

    # セッションステートの初期化

    if 'my_team' not in st.session_state:

        st.session_state.my_team = pd.DataFrame(columns=['名前', '最高戦力', '属性', 'レベル'])

    if 'opponent_team' not in st.session_state:

        st.session_state.opponent_team = pd.DataFrame(columns=['ギルド名', '名前', '最高戦力', '属性'])

    # ギルドメンバー登録フォーム

    st.header("自チームメンバー登録")

    with st.form(key='my_team_form'):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input("名前", key="my_name")

            max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="my_power")

        with col2:

            attribute = st.selectbox("属性", ["火", "水", "木"], key="my_attribute")

            level = st.number_input("レベル", min_value=1, max_value=200, value=200, step=1, key="my_level")

        submit_button = st.form_submit_button(label='自チームに登録')

    if submit_button:

        new_data = pd.DataFrame({

            '名前': [name],

            '最高戦力': [f"{max_power}万"],

            '属性': [attribute],

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

        with col2:

            max_power = st.number_input("最高戦力", min_value=0.0, step=0.1, key="opp_power")

            attribute = st.selectbox("属性", ["火", "水", "木"], key="opp_attribute")

        submit_button = st.form_submit_button(label='対戦相手チームに登録')

    if submit_button:

        new_data = pd.DataFrame({

            'ギルド名': [guild_name],

            '名前': [name],

            '最高戦力': [f"{max_power}万"],

            '属性': [attribute]

        })

        st.session_state.opponent_team = pd.concat([st.session_state.opponent_team, new_data], ignore_index=True)

    # 自チームと対戦相手チームのデータ表示

    st.subheader("自チームメンバー")

    st.dataframe(st.session_state.my_team)

    st.subheader("対戦相手チームメンバー")

    st.dataframe(st.session_state.opponent_team)

    # デバフ逆算

    if not st.session_state.my_team.empty and not st.session_state.opponent_team.empty:

        st.header("デバフ逆算")

        all_results = []

        for _, opponent in st.session_state.opponent_team.iterrows():

            st.subheader(f"対戦相手: {opponent['名前']} (戦力: {opponent['最高戦力']}, 属性: {opponent['属性']})")

            opponent_power = float(opponent['最高戦力'].rstrip('万'))

            results = []

            for _, ally in st.session_state.my_team.iterrows():

                ally_power = float(ally['最高戦力'].rstrip('万'))

                required_kills = calculate_required_kills(ally_power, opponent_power, ally['属性'], opponent['属性'])

                results.append({

                    '名前': ally['名前'],

                    '戦力': ally['最高戦力'],

                    '属性': ally['属性'],

                    '必要KILL数': required_kills

                })

            # 必要KILL数が少ない順に並べ替え

            results_df = pd.DataFrame(results)

            results_df = results_df.sort_values('必要KILL数')

            # 上位3名を表示

            top_results = results_df.head(3)

            st.write("攻撃メンバー（必要KILL数順）：")

            for _, row in top_results.iterrows():

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
 
