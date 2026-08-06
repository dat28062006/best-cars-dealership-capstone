import React, { useState } from "react";

import Header from "../Header/Header";
import emailIcon from "../assets/email.png";
import passwordIcon from "../assets/password.png";
import personIcon from "../assets/person.png";
import "./Register.css";

const Register = () => {
  const [userName, setUserName] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const register = async (event) => {
    event.preventDefault();
    const response = await fetch("/djangoapp/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userName, firstName, lastName, email, password }),
    });
    const result = await response.json();
    if (result.status === "Authenticated") {
      sessionStorage.setItem("username", result.userName);
      sessionStorage.setItem("firstname", result.firstName);
      sessionStorage.setItem("lastname", result.lastName);
      window.location.href = "/dealers/";
    } else {
      alert(result.message || "Registration failed");
    }
  };

  return (
    <div><Header /><form className="register_container" onSubmit={register}>
      <h1 className="header">Create account</h1>
      <div className="inputs">
        <label className="input" htmlFor="username"><img src={personIcon} className="img_icon" alt="" /><input id="username" name="userName" className="input_field" aria-label="Username" placeholder="Username" value={userName} onChange={(e) => setUserName(e.target.value)} required /></label>
        <label className="input" htmlFor="firstname"><img src={personIcon} className="img_icon" alt="" /><input id="firstname" name="firstName" className="input_field" aria-label="First Name" placeholder="First Name" value={firstName} onChange={(e) => setFirstName(e.target.value)} required /></label>
        <label className="input" htmlFor="lastname"><img src={personIcon} className="img_icon" alt="" /><input id="lastname" name="lastName" className="input_field" aria-label="Last Name" placeholder="Last Name" value={lastName} onChange={(e) => setLastName(e.target.value)} required /></label>
        <label className="input" htmlFor="email"><img src={emailIcon} className="img_icon" alt="" /><input id="email" name="email" className="input_field" type="email" aria-label="Email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
        <label className="input" htmlFor="password"><img src={passwordIcon} className="img_icon" alt="" /><input id="password" name="password" className="input_field" type="password" aria-label="Password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
      </div>
      <div className="submit_panel"><button className="submit" type="submit">Register</button></div>
    </form></div>
  );
};

export default Register;
