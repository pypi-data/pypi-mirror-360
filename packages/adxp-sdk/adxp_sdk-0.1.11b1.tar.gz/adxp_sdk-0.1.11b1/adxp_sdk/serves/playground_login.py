login_html = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }}
        
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #0c0e14;
            color: #ffffff;
        }}
        
        .container {{
            width: 600px;
            max-width: 90%;
        }}
        
        .header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .logo-text {{
            font-size: 20px;
            font-weight: 600;
            margin-left: 8px;
        }}
        
        .login-container {{
            background-color: #151924;
            border-radius: 8px;
            padding: 24px;
        }}
        
        .login-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
        }}
        
        .form-group {{
            margin-bottom: 16px;
        }}
        
        input {{
            width: 100%;
            padding: 10px 12px;
            background-color: #1c202e;
            border: 1px solid #2a2f3b;
            border-radius: 4px;
            color: #ffffff;
            font-size: 14px;
        }}
        
        input:focus {{
            outline: none;
            border-color: #3d4354;
        }}
        
        input::placeholder {{
            color: #6b7280;
        }}
        
        button {{
            width: 100%;
            padding: 10px 12px;
            background-color: #2c3142;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        button:hover {{
            background-color: #3d4354;
        }}
        
        .reset-button {{
            text-align: right;
            margin-bottom: 12px;
        }}
        
        .reset-link {{
            color: #6b7280;
            font-size: 14px;
            text-decoration: none;
        }}
        
        .reset-link:hover {{
            color: #ffffff;
        }}
        
        .error-message {{
            color: #f87171;
            margin-top: 12px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span>🦜</span>
            <span class="logo-text">LangServe</span>
        </div>
        <div class="login-container">
            <div class="login-title">로그인</div>
            <div class="reset-button">
                <a href="#" class="reset-link">초기화</a>
            </div>
            <form action="{root_path}/login" method="post">
                <div class="form-group">
                    <input type="text" name="api_key" placeholder="API 키를 입력하세요" required>
                </div>
                <div class="form-group">
                    <input type="text" name="aip_user" placeholder="사용자 이름을 입력하세요" required>
                </div>
                <div class="form-group">
                    <input type="text" name="aip_app_serving_id" placeholder="서빙 ID를 입력하세요(optional)">
                </div>
                <div class="form-group">
                    <input type="text" name="prefix" placeholder="route_prefix를 입력하세요(optional)" value="">
                </div>
                <button type="submit">로그인</button>
            </form>
            <div class="error-message">{error_message}</div>
        </div>
    </div>
</body>
</html>"""
