# 2024/09/02
# 中間実験完成系
# API節約のために応答を固定する
# 応答をmemo.txtに保存

import openai
import os
import streamlit as st
import subprocess
from io import StringIO
import tempfile

st.title("応答を固定化（API節約）")

# 自作したrole: systemのプロンプト（適宜変更）
# user_prompt = ''にする（プロンプト１）
# self_sys_prompt = ""

# user_prompt = 'プログラムのエラーを説明してください'にする（２〜７）
# self_sys_prompt = "プログラムのエラーを説明してください。コードは含めないでください。"
# self_sys_prompt = "プログラムのエラーを丁寧に説明してください。コードは含めないでください。"
# self_sys_prompt = "プログラムのエラーの解説と、エラーの修正方法を、2段階に分けて説明してください。コードは含めないでください。"
# self_sys_prompt = "プログラムのエラーを説明してください。"
# self_sys_prompt = "プログラムのエラーを丁寧に説明してください。"
# self_sys_prompt = "プログラムのエラーの解説と、エラーの修正方法を、2段階に分けて説明してください。"

# 追加プロンプト（8）
self_sys_prompt = "最初に直すべき場所を１つだけ挙げてください。"

# 自作したrole: userのプロンプト（基本的に変更しない）
# user_prompt = ''
user_prompt = 'プログラムのエラーを説明してください'


# 内容コピー先のファイルを指定
memo_file_path = 'memo.txt'

# 生成された応答を格納する変数
full_response = ""


# 応答内容をコピーする関数：append_to_file
def append_to_file(file_path, text):
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(text + '\n' + '\n')

# 応答を生成する関数：response_generation
def response_generation(self_user_prompt, pf):
    # 自作のプロンプトを追加
    pf += self_user_prompt

    st.markdown("現在の出力")
    message_placeholder = st.empty()
    full_response = "実験用に応答を生成させないよ！調子はどうかな？"
    ####### 応答固定化のためにコメントアウト
    # for response in openai.ChatCompletion.create(
    #     model = st.session_state["openai_model"],

    #     messages = [
            
    #         # {"role": m["role"], "content": m["content"]}
    #         # for m in st.session_state.messages
    #         # role: systemを適宜変更
    #         {"role": "system", "content": self_sys_prompt},
    #         {"role": "user", "content": pf}
    #     ],
    #     stream = True,
    # ):
    #     full_response += response.choices[0].delta.get("content", "")
    #     message_placeholder.markdown(full_response + " ")
    message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    append_to_file(memo_file_path, '--------------------------------------------------')
    append_to_file(memo_file_path, '----------------ここから新しいファイル----------------')
    append_to_file(memo_file_path, '--------------------------------------------------')
    pf += '\n'
    pf += '----------------ここから生成された応答----------------\n'
    pf += full_response # 生成された解説を追加
    append_to_file(memo_file_path, pf)

# 入力格納用リスト
lis = []

openai.api_key = 'sk-'

# "openai_model"作成
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

# "messages"作成
if "messages" not in st.session_state:
    st.session_state.messages = []

# 以前のメッセージを表示
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            
            st.markdown("過去の入力")
            # st.markdown(message["content"])
            st.code(message["content"], language='java')
            lis.append(message["content"])

    if message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown("過去の出力")
            st.markdown(message["content"])

# uploaded_file = st.file_uploader("Javaファイルをアップロードしてください", type=["java"])
uploaded_file = st.sidebar.file_uploader("Javaファイルをアップロードしてください", type=["java"])

if uploaded_file is not None:
    # アップロードされたファイルの名前を取得
    file_name = uploaded_file.name
    st.write(f"アップロードされたファイルの名前: {file_name}")
    # st.session_state.fn.append(file_name) # ファイル名追加

    string_data = '// ' + file_name + '\n'

    # prompt格納用
    prompt_full = ''

    try:
        # 一時ディレクトリを作成
        with tempfile.TemporaryDirectory() as temp_dir:
            # アップロードされたファイルの内容を指定された名前で一時ファイルに保存
            temp_file_path = os.path.join(temp_dir, file_name)
            print('ファイルが入力されました')

            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(uploaded_file.read())

                # 中身表示 #

                # To convert to a string based IO:
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                # st.write(stringio)

                # To read file as string:
                string_data += stringio.read()
                # st.write(string_data)

                prompt_full += string_data + '\n'

                with st.chat_message("user"):
                    st.markdown("現在の入力")
                    st.code(string_data, language='java')
                    # st.markdown(string_data)

            print(f"アップロードされたファイルは一時ファイルに保存されました: {temp_file_path}")

            # javacコマンドを実行
            result = subprocess.run(["javac", temp_file_path], capture_output=True, text=True)
            # st.write(f"実行したコマンド: javac {temp_file_path}")
            print("result.returncode: ", result.returncode)

            # コンパイル結果を表示
            if result.returncode == 0:
                st.success("コンパイル成功")

                javaresult = subprocess.run(["java", temp_file_path], capture_output=True, text=True) # javaする
                jacode = javaresult.returncode # javaのreturncode
                out = javaresult.stdout # java実行結果
                jaerr = javaresult.stderr # 実行時エラー

                print('コンパイル成功')

                if (jacode == 0): # 実行成功
                    st.write('実行結果:')
                    st.write(out)

                    setumei = '正常にコンパイルできました' + '\n' + '実行結果' + '\n' + out
                    
                    st.session_state.messages.append({"role": "user", "content": string_data})
                    st.session_state.messages.append({"role": "assistant", "content": setumei}) 

                    print('正しく実行できました')
                    print(out)
                    print(setumei)

                else: # 実行失敗
                    st.error('実行失敗')
                    string_data += jaerr

                    # st.session_state.messages.append({"role": "user", "content": string_data})

                    # 応答生成
                    prompt_full += jaerr
                    st.session_state.messages.append({"role": "user", "content": prompt_full})
                    # role: userを変更かも
                    # prompt_full += 'エラーの原因を1文で簡単に説明してください'
                    

                    print('実行時エラーが出ましたよ')
                    print(jaerr)

                    print('javaのprompt_full')
                    print(prompt_full)

                    with st.chat_message("assistant"):
                        # ここで関数を呼び出す
                        response_generation(user_prompt, prompt_full)
                    
                
            else:
                err = result.stderr
                prompt_full += err

                st.error("コンパイル失敗")
                st.write("標準エラー出力:")
                st.text(result.stderr)

                print('コンパイル失敗')
                print('result.stderr', err)

                # 「過去の入力」にプログラム本体とエラー文追加
                st.session_state.messages.append({"role": "user", "content": prompt_full})
                
                print('javacのprompt_full')
                print(prompt_full)

                with st.chat_message("assistant"):
                    # 応答生成する関数呼び出し
                    response_generation(user_prompt, prompt_full)

    except Exception as e:
        st.error("予期せぬエラーが発生しました")
        st.error(str(e))
