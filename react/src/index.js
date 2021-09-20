import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { IoIosPin } from "react-icons/io";
import { MdCall } from "react-icons/md";

ReactDOM.render(
  <React.StrictMode>
    <App />
    <footer className="footer">
      <small><b>Question Group Generator</b> by Philip Huang</small>
      <hr />
      <small>
      <IoIosPin/> 中興大學，理學大樓721室 NLP LAB<br />
      <MdCall/> 04-22840497轉721
      </small>
      <br />
    </footer>
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
