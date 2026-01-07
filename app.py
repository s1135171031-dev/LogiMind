# app.py 中的 page_lab 替換為以下內容：

def page_lab(uid, user):
    st.title("🔬 數位邏輯實驗室 (Digital Logic Lab)")
    st.caption("CityOS 硬體開發模擬環境 v2.0")

    # 1. 選擇元件
    col1, col2 = st.columns([1, 2])
    with col1:
        gate = st.selectbox("選擇邏輯閘 (Logic Gate)", list(SVG_LIB.keys()))
        
        # 顯示元件說明
        descriptions = {
            "AND": "邏輯「及」：兩者皆為 1，輸出才為 1。",
            "OR": "邏輯「或」：任一為 1，輸出即為 1。",
            "NOT": "邏輯「非」：反轉輸入信號 (1變0, 0變1)。",
            "XOR": "互斥或：兩者不同時，輸出為 1。",
            "NAND": "反及閘：AND 的相反。SSD 快閃記憶體的基礎。",
            "NOR": "反或閘：OR 的相反。通用邏輯閘之一。",
            "XNOR": "互斥反或：兩者相同時，輸出為 1 (同位檢查)。"
        }
        st.info(descriptions.get(gate, ""))

    with col2:
        # 顯示 SVG 圖示
        st.markdown(f"<div style='text-align: center; margin: 20px;'>{SVG_LIB[gate]}</div>", unsafe_allow_html=True)

    st.divider()

    # 2. 互動測試區 & 真值表並排
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("⚡ 訊號測試")
        st.write("調整輸入以觀察輸出變化：")
        
        # 輸入開關
        input_a = st.toggle("Input A (輸入 A)", value=False)
        input_b = False
        if gate != "NOT": # NOT 只有一個輸入
            input_b = st.toggle("Input B (輸入 B)", value=False)
        
        # 計算結果
        out = False
        if gate == "AND": out = input_a and input_b
        elif gate == "OR": out = input_a or input_b
        elif gate == "NOT": out = not input_a
        elif gate == "XOR": out = input_a != input_b
        elif gate == "NAND": out = not (input_a and input_b)
        elif gate == "NOR": out = not (input_a or input_b)
        elif gate == "XNOR": out = input_a == input_b

        # 顯示結果 (大字體)
        if out:
            st.success(f"Output: 1 (High)")
        else:
            st.error(f"Output: 0 (Low)")

    with c2:
        st.subheader("📋 真值表 (Truth Table)")
        st.write(f"元件 **{gate}** 的完整邏輯定義：")
        
        # 自動生成真值表
        table_data = []
        if gate == "NOT":
            inputs = [(0,), (1,)]
            cols = ["Input A", "Output"]
        else:
            inputs = [(0,0), (0,1), (1,0), (1,1)]
            cols = ["Input A", "Input B", "Output"]

        for row in inputs:
            a = bool(row[0])
            b = bool(row[1]) if len(row) > 1 else False
            
            res = False
            if gate == "AND": res = a and b
            elif gate == "OR": res = a or b
            elif gate == "NOT": res = not a
            elif gate == "XOR": res = a != b
            elif gate == "NAND": res = not (a and b)
            elif gate == "NOR": res = not (a or b)
            elif gate == "XNOR": res = a == b
            
            # 將 True/False 轉回 1/0 以符合工程習慣
            r_data = [1 if x else 0 for x in row]
            r_data.append(1 if res else 0)
            table_data.append(r_data)

        # 顯示漂亮的表格
        df = pd.DataFrame(table_data, columns=cols)
        
        # 標記當前狀態 (Highligt current state)
        def highlight_current(s):
            is_match = False
            if gate == "NOT":
                if s["Input A"] == int(input_a): is_match = True
            else:
                if s["Input A"] == int(input_a) and s["Input B"] == int(input_b): is_match = True
            
            return ['background-color: #004400' if is_match else '' for _ in s]

        st.dataframe(df.style.apply(highlight_current, axis=1), use_container_width=True, hide_index=True)
