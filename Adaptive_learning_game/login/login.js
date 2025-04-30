document.getElementById("adaptive").addEventListener("submit", async function(event) {
    event.preventDefault();

    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    let fullNameField = document.getElementById("name");
    let isSignup = fullNameField.style.display !== "none";

    let data = {
        username: username,
        password: password
    };

    if (isSignup) {
        data.full_name = fullNameField.value;
    }

    const endpoint = isSignup ? "/signup" : "/login";

    try {
        const response = await fetch(`http://127.0.0.1:5000${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message);

            if (isSignup) {
                document.getElementById("form-title").innerText = "Login";
                fullNameField.style.display = "none";
                document.querySelector(".btn").innerText = "Login";
                document.getElementById("signup-text").style.display = "block";
                document.getElementById("toggle-text").style.display = "none";
                document.getElementById("adaptive").reset();
                
            } else {
                sessionStorage.setItem("username", username);
                window.location.href = "index.html";
            }
        } else {
            alert(result.error || "Something went wrong!");
        }

    } catch (error) {
        console.error("Error:", error);
        alert("There was an issue with the request.");
    }
});

function toggleForm() {
    const title = document.getElementById("form-title");
    const fullNameField = document.getElementById("name");
    const button = document.querySelector(".btn");
    const signupText = document.getElementById("signup-text");
    const toggleText = document.getElementById("toggle-text");

    const isLogin = title.innerText === "Login";

    if (isLogin) {
        // Switch to Sign Up form
        title.innerText = "Sign Up";
        fullNameField.style.display = "block";
        button.innerText = "Sign Up";
        signupText.style.display = "none";
        toggleText.style.display = "block";
    } else {
        // Switch to Login form
        title.innerText = "Login";
        fullNameField.style.display = "none";
        button.innerText = "Login";
        signupText.style.display = "block";
        toggleText.style.display = "none";
    }

}
