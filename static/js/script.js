let chart;

document.getElementById("form").onsubmit = async function (e) {
e.preventDefault();

const data = {
    age: +age.value,
    bmi: +bmi.value,
    children: +children.value,
    sex: sex.value,
    smoker: smoker.value,
    region: region.value,
};

const res = await fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
});

const result = await res.json();

if (result.error) {
    alert(result.error);
    return;
}

  // ==========================
// VALIDASI INPUT
// ==========================
if (data.age <= 0) {
    alert("Umur harus lebih dari 0");
    return;
}

if (data.bmi <= 0) {
    alert("BMI harus lebih dari 0");
    return;
}

if (data.bmi < 10 || data.bmi > 60) {
    alert("BMI tidak realistis (10 - 60)");
    return;
}

const pred = result.prediction;
const lower = result.range.lower;
const upper = result.range.upper;

  // tampilkan angka
prediction.innerText = "$ " + pred.toFixed(0);
range.innerText = `Range: $ ${lower.toFixed(0)} - $ ${upper.toFixed(0)}`;

  // indikator risiko
let riskText, color;
if (pred < 4000) {
    riskText = "🟢 Risiko Rendah";
    color = "lightgreen";
} else if (pred < 10000) {
    riskText = "🟡 Risiko Sedang";
    color = "yellow";
} else {
    riskText = "🔴 Risiko Tinggi";
    color = "red";
}

risk.innerText = riskText;
risk.style.color = color;

  // grafik
if (chart) chart.destroy();

const ctx = document.getElementById("chart");

  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Min", "Prediksi", "Max"],
      datasets: [
        {
          label: "Biaya",
          data: [lower, pred, upper],
        },
      ],
    },
  });

  // ==========================
  // INSIGHT RISIKO
  // ==========================
  const riskBox = document.getElementById("risk-box");
  riskBox.innerHTML = "";

  let risks = [];

  // BMI
  if (data.bmi < 18.5) {
    risks.push({ text: "BMI rendah (underweight)", level: "medium" });
  } else if (data.bmi >= 25 && data.bmi < 30) {
    risks.push({ text: "BMI overweight", level: "medium" });
  } else if (data.bmi >= 30) {
    risks.push({
      text: "BMI obesitas meningkatkan risiko kesehatan",
      level: "high",
    });
  }

  // Smoker
  if (data.smoker === "yes") {
    risks.push({
      text: "Merokok sangat meningkatkan biaya asuransi",
      level: "high",
    });
  }

  // Age
  if (data.age > 50) {
    risks.push({
      text: "Usia di atas 50 meningkatkan risiko",
      level: "medium",
    });
  }

  // Children (opsional insight ringan)
  if (data.children >= 3) {
    risks.push({
      text: "Jumlah tanggungan tinggi dapat mempengaruhi biaya",
      level: "low",
    });
  }

  // ==========================
  // TAMPILKAN
  // ==========================
  if (risks.length === 0) {
    riskBox.innerHTML = "<p>✅ Risiko relatif rendah</p>";
  } else {
    risks.forEach((r) => {
      const div = document.createElement("div");
      div.className = `risk-item ${r.level}`;
      div.innerText = r.text;
      riskBox.appendChild(div);
    });
  }
};
