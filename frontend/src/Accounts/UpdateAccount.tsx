import React, { useState } from "react";
import { logout, getGroups, getUsers } from "../Utils/ApiUtils";
import { Link } from "react-router-dom";

import "./UpdateAccount.css"

/**
 * Functional component for updating user accounts.
 * @returns {JSX.Element} JSX element representing the UpdateAccount component.
 */
export default function UpdateAccount() {
  // Retrieve the user token from local storage
  let token = localStorage.getItem('token') as string

  // State to store the list of groups and users
  const [groups, setGroups] = useState([""]);
  const [users, setUsers] = useState([""]);

  // Fetch groups and update the state if it's empty
  if (groups[0] === "") {
    getGroups(token).then((result) => {
      setGroups(result)
    });
  }

  // Fetch users and update the state if it's empty
  if (users[0] === "") {
    getUsers(token).then((result) => {
      // Map the user objects to strings containing id and login
      setUsers(result.map(user => `${user.id}:${user.login}`));
    });
  }
  
  
  return (
    <>
      <div className="header">
        <h1>Update user account</h1>
        <button onClick={logout}>log out</button>
      </div>

      <div className="choose-user-container">
        <p>Choose user:</p>
        <select name="users" id="users">
         <option disabled selected hidden> select user </option>
          {
            users.map((item) =>
            <option value={item}>{item}</option>
          )}
        </select>
      </div>  
        
      <div className="update-account-form">
        <form>
          <div className="input-field">
            <label htmlFor="login">Insert new login:</label>
            <input type="text" name="login" id="login" />
          </div>
          <div className="input-field">
            <label htmlFor="password">Insert new password:</label>
            <input type="text" name="password" id="password" />
          </div>
          <div className="input-field">
            <p>Select new group:</p>
            <select name="users" id="users">
            <option disabled selected hidden> select group </option>
             {groups.map((item) => 
              <option value={item}>{item}</option>
              )}
            </select>
          </div>
        </form>
      </div>
      
      <div className="save-changes-button">
        <button>
          Save changes
        </button>
      </div>

      <div className="back-button">
        <Link to="/" >
          Back
        </Link>
      </div>
    </>
  );
}
