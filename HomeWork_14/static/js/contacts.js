async function local_sort_table(col_num, type, id) {
  // let elem = document.getElementById(id);
  // let tbody = elem.querySelector("tbody");
  // let rows_array = Array.from(tbody.rows);
  // let compare;
  // switch(type) {
  //   case "number":
  //     compare = function(row_a, row_b) {
  //       return row_a.cells[col_num].innerHTML - row_b.cells[col_num].innerHTML;
  //     }
  //   break;
  //   case "string":
  //     compare = function(row_a, row_b) {
  //       return row_a.cells[col_num].innerHTML > row_b.cells[col_num].innerHTML ? 1 : -1;
  //     }
  //   break;
  // }
  // rows_array.sort(compare);
  // tbody.append(...rows_array);
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
  td.innerHTML = contact.full_name;
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
  button.onclick = async function() {
    await EditContactShow(contact.id);
  }
  td.append(button);
  tr.append(td);

  td = document.createElement("td");
  button = document.createElement("button");
  button.className = "btn btn-outline-secondary btn-delete";
  button.innerHTML = "<span class=\'btn-label\'><i class=\'fa fa-user-minus\'></i></span>";
  button.setAttribute("style", "--bs-btn-padding-y: .2rem; --bs-btn-padding-x: .5rem; " +
    "--bs-btn-font-size: .75rem;");
  button.onclick = async function() {
    await DeleteContactShow(contact.id);
  }

  td.append(button);
  tr.append(td);

  return tr;
}

async function getContacts(filter_type=0) {
  let filter_str;
  if (filter_type === 1)
    filter_str = document.getElementById("filter_str").value;

  const url_str = `/api/contacts/?filter_type=${filter_type}&filter_str=${filter_str}`
  const token = localStorage.getItem('accessToken');

  const response = await fetch(url_str, {
    method: "GET",
    headers: {
      "Accept": "application/json",
      Authorization: `Bearer ${token}`,
    }
  });
  if (response.ok === true) {
    const contacts = await response.json();
    const rows = document.querySelector("tbody");

    while (rows.rows.length)
      rows.deleteRow(0);

    contacts.forEach(contact => rows.append(new_table_row(contact)));
  }
  else{
    if (response.status === 401)
      alert("Not authenticated");
    else {
      const error = await response.json();
      alert(error.detail);
    }
  }
}

function phones_to_str (contact_phones) {
  let phones_str = "";
  if (contact_phones) {
    let phone_list = [];
    for (let phone of contact_phones) {
      phone_list.push(phone["phone_num"])
    }
    phones_str = phone_list.join(", ");
  }
  return phones_str;
}

function str_to_phones (phones_str) {
  const phones = [];
  const phone_list = phones_str.split(",").map(x => x.trim());
  for (let phone of phone_list) {
    if (phone) {
      phones.push({"phone_num": phone})
    }
  }
  return phones;
}

async function getContact(id) {
  const token = localStorage.getItem('accessToken');

  return(await fetch(`/api/contacts/${id}`, {
    method: "GET",
    headers: {
      "Accept": "application/json",
      Authorization: `Bearer ${token}`,
    }
  }));
}


async function editContact(cnt_id) {
  const birthday = document.getElementById("birthday").value;
  const last_name = document.getElementById("last_name").value;
  const address = document.getElementById("address").value;

  const token = localStorage.getItem('accessToken');

  const response = await fetch(`/api/contacts/${cnt_id}`, {
    method: (cnt_id === "" ? "POST" : "PUT"),
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      first_name: document.getElementById("first_name").value,
      last_name: last_name ? last_name : null,
      birthday: birthday ? birthday : null,
      email: document.getElementById("email").value,
      phones: str_to_phones(document.getElementById("phones").value),
      address: address ? address : null
    })
  });
  if (response.ok === true) {
    const contact = await response.json();
    if (cnt_id === "")
      document.querySelector("tbody").append(new_table_row(contact));
    else
      document.querySelector(`tr[data-rowid='${contact.id}']`).replaceWith(new_table_row(contact));
  }
  else {
    if (response.status === 401)
      alert("Not authenticated");
    else if (response.status === 422)
      alert("Input data is invalid");
    else {
      const error = await response.json();
      alert(error.detail);
    }
  }
  return response.ok;
}

async function deleteContact(id) {
  const token = localStorage.getItem('accessToken');

  const response = await fetch(`/api/contacts/${id}`, {
    method: "DELETE",
    headers: {
      "Accept": "application/json",
      Authorization: `Bearer ${token}`
    },

  });
  if (response.ok === true) {
    document.querySelector(`tr[data-rowid='${id}']`).remove();
  }
  else {
    if (response.status === 401)
      alert("Not authenticated");
    else {
      const error = await response.json();
      alert(error.detail);
    }
  }
  return response.ok;
}

async function DeleteContactShow(cnt_id) {
  const modal_form = document.getElementById("DeleteContact")
  const modal = new bootstrap.Modal(modal_form);

  const submit_btn = modal_form.querySelector(".btn-danger");
  submit_btn.onclick = async function () {
    if (await deleteContact(cnt_id))
      modal.hide();
  };
  modal.show();
}

async function EditContactShow(cnt_id) {
  const modal_form = document.getElementById("EditContact")
  const modal = new bootstrap.Modal(modal_form);
  if (cnt_id === "") {
    modal_form.querySelector("#first_name").value = "";
    modal_form.querySelector("#last_name").value = "";
    modal_form.querySelector("#birthday").value = "";
    modal_form.querySelector("#email").value = "";
    modal_form.querySelector("#phones").value = "";
    modal_form.querySelector("#address").value = "";
  }
  else{
    const response = await getContact(cnt_id);
    if (response.ok === true) {
      const contact = await response.json();
      modal_form.querySelector("#first_name").value = contact.first_name;
      modal_form.querySelector("#last_name").value = contact.last_name;
      modal_form.querySelector("#birthday").value = contact.birthday;
      modal_form.querySelector("#email").value = contact.email;
      modal_form.querySelector("#phones").value = phones_to_str(contact.phones);
      modal_form.querySelector("#address").value = contact.address;
    } else {
      const error = await response.json();
      alert(error.detail);
      return;
    }
  }

  const submit_btn = modal_form.querySelector(".btn-primary");
  submit_btn.onclick = async function () {
    if (await editContact(cnt_id))
      modal.hide();
  };
  modal.show();
}
