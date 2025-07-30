def get_html_code(server_url: str, state: str):
    return (
        """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Simple MCP Authentication</title>
    <style>
        /* Reset básico */
        * {
            box-sizing: border-box;
        }

        body {
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 400px;
            margin: 40px auto;
            padding: 30px 25px;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0,0,0,0.7);
        }

        h2 {
            text-align: center;
            margin-bottom: 10px;
            font-weight: 600;
            color: #bb86fc;
        }

        p {
            text-align: center;
            margin-bottom: 25px;
            color: #bbbbbb;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 6px;
            font-weight: 500;
            color: #cccccc;
        }

        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 12px 15px;
            border: 1.5px solid #333;
            border-radius: 6px;
            background-color: #1e1e1e;
            color: #eee;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }

        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: #bb86fc;
            outline: none;
            background-color: #2a2a2a;
        }

        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #bb86fc, #6200ee);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(187, 134, 252, 0.5);
            transition: background 0.3s ease;
        }

        button:hover {
            background: linear-gradient(135deg, #9f6efb, #3700b3);
        }

        /* Para dispositivos móviles */
        @media (max-width: 480px) {
            body {
                margin: 20px 15px;
                padding: 25px 20px;
            }
        }
    </style>
</head>"""
        + f"""
<body>
    <h2>Simple MCP Authentication</h2>
    <p>Enter your credentials</p>
    <form action="{server_url.rstrip('/')}/login/callback" method="post">
        <input type="hidden" name="state" value="{state}">
        <div class="form-group">
            <label for="username">Username:</label>
            <input id="username" type="text" name="username" value="demo_user" required autocomplete="username" />
        </div>
        <div class="form-group">
            <label for="password">Password:</label>
            <input id="password" type="password" name="password" value="demo_password" required autocomplete="current-password" />
        </div>
        <button type="submit">Sign In</button>
    </form>
</body>
</html>
"""
    )
