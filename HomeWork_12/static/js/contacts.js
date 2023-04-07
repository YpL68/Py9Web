async function local_sort_table(col_num, type, id) {
  let elem = document.getElementById(id);
  let tbody = elem.querySelector("tbody");
  let rows_array = Array.from(tbody.rows);
  let compare;
  switch(type) {
    case "number":
      compare = function(row_a, row_b) {
        return row_a.cells[col_num].innerHTML - row_b.cells[col_num].innerHTML;
      }
    break;
    case "string":
      compare = function(row_a, row_b) {
        return row_a.cells[col_num].innerHTML > row_b.cells[col_num].innerHTML ? 1 : -1;
      }
    break;
  }
  rows_array.sort(compare);
  tbody.append(...rows_array);
}

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
  button.className = "btn btn-outline-secondary btn-edit";
  button.innerHTML = "<span class=\'btn-label\'><i class=\'fa fa-user-edit\'></i></span>";
  button.setAttribute("style", "--bs-btn-padding-y: .2rem; --bs-btn-padding-x: .5rem; " +
    "--bs-btn-font-size: .75rem;");
  button.setAttribute("data-bs-toggle", "modal");
  button.setAttribute("data-bs-target", "#EditContact");
  button.setAttribute("data-bs-cnt_id", contact.id);
  td.append(button);
  tr.append(td);

  td = document.createElement("td");
  button = document.createElement("button");
  button.className = "btn btn-outline-secondary btn-delete";
  button.innerHTML = "<span class=\'btn-label\'><i class=\'fa fa-user-minus\'></i></span>";
  button.setAttribute("style", "--bs-btn-padding-y: .2rem; --bs-btn-padding-x: .5rem; " +
    "--bs-btn-font-size: .75rem;");
  button.setAttribute("data-bs-toggle", "modal");
  button.setAttribute("data-bs-target", "#DeleteContact");
  button.setAttribute("data-bs-cnt_id", contact.id);
  td.append(button);
  tr.append(td);

  return tr;
}

async function getContacts() {
  const response = await fetch("/api/contacts", {
    method: "GET",
    headers: {"Accept": "application/json"}
  });
  if (response.ok === true) {
    const contacts = await response.json();
    const rows = document.querySelector("tbody");

    while (rows.rows.length)
      rows.deleteRow(0);

    contacts.forEach(contact => rows.append(new_table_row(contact)));
  }
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

function DeleteContactOnShow() {
  const del_form = document.getElementById("DeleteContact")

  del_form.addEventListener("show.bs.modal", async event => {
    const button = event.relatedTarget
    const cnt_id = button.getAttribute("data-bs-cnt_id")
    const submit_btn = del_form.querySelector(".btn-danger")
    const cancel_btn = del_form.querySelector(".btn-secondary")

    submit_btn.onclick = async function () {
      const result = await deleteContact(cnt_id);
      if (result)
        cancel_btn.click();
    };
  })
}

function EditContactOnShow() {
  const edit_form = document.getElementById("EditContact")

  edit_form.addEventListener("show.bs.modal", async event => {
    const button = event.relatedTarget;
    const cnt_id = button.getAttribute("data-bs-cnt_id");

    if (cnt_id === "") {
      document.getElementById("cnt_id").value = "";
      document.getElementById("first_name").value = "";
      document.getElementById("last_name").value = "";
      document.getElementById("birthday").value = "";
      document.getElementById("email").value = "";
      document.getElementById("address").value = "";
    }
    else
      await getContact(cnt_id);

    const submit_btn = edit_form.querySelector(".btn-primary");
    const cancel_btn = edit_form.querySelector(".btn-secondary");

    submit_btn.onclick = async function () {
      let result;
      if (cnt_id === "")
        result = await createContact();
      else
        result = await editContact();
      if (result)
        cancel_btn.click();
    };
  })
}


