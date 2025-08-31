import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import styles from "./Register.module.css";

const Register = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();
    const handleRegister = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post("/users/register", {email, password});
            alert("Registration Successful");
        } catch (error) {
            alert("Error Registering")
        }
    };

    const BackToLogin = () => {
        navigate("/login");
    }

    return (

        <div className={styles.RegisterpageTitle}>
            <h2>Register</h2>
            <form onSubmit = {handleRegister}>
                <input
                    type = "email"
                    value = {email}
                    onChange = {(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    required
                />
                <input
                    type = "password"
                    value = {password}
                    onChange = {(e) => setPassword(e.target.value)}
                    placeholder = "Password"
                    required
                />
                <button type = "submit">Submit</button>
                <button type = "return" onClick={BackToLogin}>Back To Login</button>
            </form>
        </div>
    );
};

export default Register;