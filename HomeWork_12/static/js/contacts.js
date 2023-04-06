function new_table_row(contact) {
  let tr = document.createElement("tr");
  tr.setAttribute("data-rowid", contact.id);
  let td = document.createElement("td");
  td.className = "text-end";
  td.innerHTML = contact.id;
  tr.append(td);
  td = document.createElement("td");
  td.className = "text-start";
  td.innerHTML = contact.first_name + (contact.last_name ? " " + contact.last_name : "");
  tr.append(td);
  td = document.createElement("td");
  td.className = "text-start";
  if (contact.birthday)
    td.innerHTML = contact.birthday.split("-").reverse().join(".");
  else
    td.innerHTML = "";
  tr.append(td);
  td = document.createElement("td");
  td.className = "text-start";
  td.innerHTML = contact.email;
  tr.append(td);

  td = document.createElement("td");

  let button = document.createElement("button");
  button.className = "btn btn-outline-secondary btn-edit btn-sm";
  button.innerHTML = "<span class=\'btn-label\'><i class=\'fa fa-user-edit\'></i></span>";
  button.setAttribute("data-bs-toggle", "modal");
  button.setAttribute("data-bs-target", "#EditContact");
  button.setAttribute("data-bs-cnt_id", contact.id);
  td.append(button);
  tr.append(td);

  td = document.createElement("td");
  button = document.createElement("button");
  button.className = "btn btn-outline-secondary btn-delete btn-sm";
  button.innerHTML = "<span class=\'btn-label\'><i class=\'fa fa-user-minus\'></i></span>";
  button.setAttribute("data-bs-toggle", "modal");
  button.setAttribute("data-bs-target", "#DeleteContact");
  button.setAttribute("data-bs-cnt_id", contact.id);
  td.append(button);
  tr.append(td);

  return tr;
}

async function getContact(id) {
  const response = await fetch(`/api/contacts/${id}`, {
    method: "GET",
    headers: {"Accept": "application/json"}
  });
  if (response.ok === true) {
    const contact = await response.json();
    document.getElementById("cnt_id").value = contact.id;
    document.getElementById("first_name").value = contact.first_name;
    document.getElementById("last_name").value = contact.last_name;
    document.getElementById("birthday").value = contact.birthday;
    document.getElementById("email").value = contact.email;
    document.getElementById("address").value = contact.address;
  } else {
    const error = await response.json();
    alert(error.message);
  }
}

async function createContact() {
  const response = await fetch("api/contacts", {
    method: "POST",
    headers: {"Accept": "application/json", "Content-Type": "application/json"},
    body: JSON.stringify({
      id: document.getElementById("cnt_id").value,
      first_name: document.getElementById("first_name").value,
      last_name: document.getElementById("last_name").value,
      birthday: document.getElementById("birthday").value,
      email: document.getElementById("email").value,
      address: document.getElementById("address").value
    })
  });
  if (response.ok === true) {
    const contact = await response.json();
    document.querySelector("tbody").append(new_table_row(contact));
  } else {
    const error = await response.json();
    alert(error.message);
    return false;
  }

  return true;
}

async function editContact() {
  const response = await fetch("api/contacts", {
    method: "PUT",
    headers: {"Accept": "application/json", "Content-Type": "application/json"},
    body: JSON.stringify({
      id: document.getElementById("cnt_id").value,
      first_name: document.getElementById("first_name").value,
      last_name: document.getElementById("last_name").value,
      birthday: document.getElementById("birthday").value,
      email: document.getElementById("email").value,
      address: document.getElementById("address").value
    })
  });
  if (response.ok === true) {
    const contact = await response.json();
    document.querySelector(`tr[data-rowid='${contact.id}']`).replaceWith(new_table_row(contact));
  } else {
    const error = await response.json();
    alert(error.message);
    return false;
  }

  return true;
}

async function deleteContact(id) {
  const response = await fetch(`/api/contacts/${id}`, {
    method: "DELETE",
    headers: {"Accept": "application/json"}
  });
  if (response.ok === true) {
    const contact = await response.json();
    document.querySelector(`tr[data-rowid='${contact.id}']`).remove();
  } else {
    const error = await response.json();
    alert(error.message);
    return false;
  }
  return true;
}
