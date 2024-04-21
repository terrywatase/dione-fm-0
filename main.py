# PS C:\Users\132632\Automation_py\streamlit\AgGrid> 
# streamlit run D1.4_FM_local.py
# mod_df をボタンで作成 ⇒ リフレッシュさせることが可能か確認

import streamlit as st
import pandas as pd
import os
import shutil
import subprocess
from datetime import datetime, timedelta


# Backend =================================================
# Presetting Formal
st.set_page_config(layout = "wide")
today = datetime.now().date()

# definition to cash
@st.cache_data
def get_file_info_to_make_dataset(folder_path):
    file_info = []  
    for root, dirs, files in os.walk(folder_path):
        for filename in files:  
            
            file_path = os.path.join(root, filename)
            size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 1) 
            file_status = os.stat(file_path) 
            
            create_time = file_status.st_ctime  
            modified_time = file_status.st_mtime  

            c_ymd = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d")
            m_ymd = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d")
                       
            file_info.append({   
                'ファイル名.タイプ': filename, 'サイズ (MB)': size_mb,
                '作成日': c_ymd, '更新日': m_ymd, 'フォルダーパス': root,
                'filepath': file_path
            })
        # making df from file info:       
        df = pd.DataFrame(file_info) # make df
        df.index = df.index + 1
        df['cbx'] = False 
       
        df = df.reindex(columns=['cbx', 'ファイル名.タイプ', 'サイズ (MB)',
                                 '作成日', '更新日',  'フォルダーパス', "filepath"])  
        df = df[df['ファイル名.タイプ'] != 'desktop.ini'] # .iniの削除
    return df


# end of Backend Server ==================================================
def edit_df(df, specified_size, passed_period):
    df['メモリ超過'] = (df["サイズ (MB)"] >= specified_size)
    df['期限超過'] = (today - pd.to_datetime(
        df['作成日']).dt.date >= timedelta(days=30 * passed_period))
    
    df['メモリ超過'] = df['メモリ超過'].map({True: '✔', False: ''})
    df['期限超過'] = df['期限超過'].map({True: '✔', False: ''})
    df = df.reindex(columns=['cbx', 'ファイル名.タイプ', 'メモリ超過', '期限超過',
                                     'サイズ (MB)', '作成日', '更新日',  
                                     'フォルダーパス', "filepath"]) 
    df = df.sort_values('サイズ (MB)', ascending=False)  # 降順並べ替え
    
    mod_df = st.data_editor(df,
            column_config={"cbx": st.column_config.CheckboxColumn(
                help = "保留ポストへ移さない場合は、チェックを外す",
                default = True)},
            disabled = ['ファイル名.タイプ', 'メモリ超過', 'サイズ (MB)', 
                        '期限超過', '作成日', '更新日', 'フォルダーパス', "filepath"],
            hide_index = True, key ="check")
 
    return mod_df


# Front top page ========================================================
st.title("Dione Filemanagent Dashboard")

# inter-face: input using form

buff, col1, buff, col2, buff = st.columns([1,30,1,10,1])



folder_path = col1.selectbox("対象フォルダを選択 (初回読込には時間がかかる場合があります):", 
                    ("\\\\inet\\PUB\\D2320_ディオネカンパニー\\D2321_ディオネカンパニー_HT課",
                     "\\\\inet\\PUB\\D2320_ディオネカンパニー\\D1853_ディオネカンパニー 第２課")) 
    
# if col1.button("フォルダーセット"): 
df = get_file_info_to_make_dataset(folder_path)


if col2.button('Cache Reset'):
    get_file_info_to_make_dataset.clear()
    
# ======================================================================
col1.divider()

specified_size = col1.slider("オーバサイズ閾値（MB 以上）: ",
                             min_value=0, max_value= 1000, value= 150, step=10)

passed_period = col2.radio("経過月数（ヶ月以上）: ", 
                           [1, 3, 6, 12, 24, 36, 48, 60], horizontal = True)


# 編集済みリストの表示 ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

mod_df = edit_df(df, specified_size, passed_period)

# 抽出結果の概要と 表示 ========================================
df1 = mod_df[(mod_df['メモリ超過'] == '✔') | (mod_df['期限超過'] == '✔')]
n = len(df) ; sel_n = len(df1) ; ratio = round((sel_n / n)*100, 1)   

col1.markdown(f"総ファイル数：{n}個,  OR 条件で抽出されたファイル数：{sel_n}個, 占有率：{ratio}％")


#  =========================================================
# チェックを入れたアイテムの抽出と表による確認
selected_files = mod_df.query("cbx == True")["filepath"].tolist()
f"チェックしたファイル数： **{len(selected_files)}**"

if selected_files:
    "選択された管理ポスト行きファイル："
    st.dataframe(selected_files, use_container_width = True)
else:
    "転送するファイルをチェックしてから「転送ボタン」を押す"



# ==========転送ボタンの設定 =================================
nozoki_btn = st.button('管理ポストを覗く')
tenso_btn = st.button("管理ポストへ転送")
# ============================================================

# 転送命令とチェックの解除命令 ===============================
kanri_post = r"\\inet\PUB\D2320_ディオネカンパニー\00_管理ポスト"

if nozoki_btn:
    popen = subprocess.Popen(["explorer", kanri_post], shell = True)
    popen.wait()

if  tenso_btn:
    for i in selected_files:
        shutil.move(i, kanri_post)
    st.write(f"管理ポストへ転送されました")
    








#st.session_state










