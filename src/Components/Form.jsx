import React, { useState, useEffect } from "react";
import { Form, Button, Modal } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner } from "@fortawesome/fontawesome-free-solid";

import myFetch from "./myFetch";
import { industries } from "./helpers";

export const AccountForm = (props) => {
  const { selectedCompany = {}, isSaving, isCreatingAnExampleCompany } = props;
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const [company, setCompany] = useState({});

  useEffect(() => {
    setCompany(
      isCreatingAnExampleCompany
        ? {
            isExampleCompany: true,
            dataSource: "facebook",
            industry: "apparel",
            property: "app",
            model: "ecommerce",
            spend: "$1-4,999",
            team: "in-house",
            location: "north_america",
          }
        : {
            ...selectedCompany,
            industry: selectedCompany.industry || "apparel",
            property: selectedCompany.property || "app",
            model: selectedCompany.model || "ecommerce",
            spend: selectedCompany.spend || "$1-4,999",
            team: selectedCompany.team || "in-house",
            location: selectedCompany.location || "north_america",
          }
    );
  }, [isCreatingAnExampleCompany]);

  const MyDropdown = (props) => {
    const handleChange = (event) => {
      const newCompany = Object.assign({}, company);
      newCompany[props.valueId] = event.target.value;
      setCompany(newCompany);
    };

    return (
      <FormItem
        name={props.name}
        key={`${selectedCompany.account_id}_${props.name}_item`}
      >
        <Form.Control
          key={`${selectedCompany.account_id}_${props.name}`}
          as="select"
          value={company[props.valueId] || ""}
          onChange={handleChange}
        >
          {props.options.map((option) => {
            const optionLabel = option
              .split("_")
              .map((word) => word[0].toUpperCase() + word.slice(1))
              .join(" ");
            return (
              <option key={option} value={option}>
                {optionLabel}
              </option>
            );
          })}
        </Form.Control>
      </FormItem>
    );
  };

  const handleTextChange = (event, id) => {
    const newCompany = Object.assign({}, company);
    newCompany[id] = event.target.value;
    setCompany(newCompany);
  };

  return (
    <MyForm
      {...props}
      key={`${selectedCompany.account_id}_form`}
      onSubmit={(event) => {
        const form = event.currentTarget;
        form.checkValidity();
        props.onSubmit(company);
      }}
    >
      <h2>Account Onboarding Form</h2>
      <p>
        Please complete this form to match to similar companies.
        {!isCreatingAnExampleCompany &&
          " Once you click save, your Facebook performance data will be anonymously benchmarked against similar companies."}
      </p>

      <div style={{ maxWidth: 400, margin: "auto" }}>
        {(isCreatingAnExampleCompany || selectedCompany?.isExampleCompany) && (
          <div>
            <FormItem
              name="Example Company Name"
              key={`${selectedCompany.account_id}_name_item`}
            >
              <Form.Control
                key={`${selectedCompany.account_id}_name`}
                type="text"
                required
                value={company["name"] || ""}
                onChange={(event) => handleTextChange(event, "name")}
              ></Form.Control>
            </FormItem>
            {isCreatingAnExampleCompany && (
              <MyDropdown
                name="Data Source"
                valueId="dataSource"
                options={["facebook", "google"]}
              />
            )}
          </div>
        )}
        <MyDropdown
          name="Closest Industry"
          valueId="industry"
          options={industries}
        />

        <MyDropdown
          name="Primary Product"
          valueId="property"
          options={["app", "website", "store"]}
        />

        <MyDropdown
          name="Business Model"
          valueId="model"
          options={[
            "ecommerce",
            "subscription",
            "sales",
            "advertising",
            "marketplace",
          ]}
        />

        <MyDropdown
          name="Monthly Spend"
          valueId="spend"
          options={[
            "$1-4,999",
            "$5,000-$9,999",
            "$10,000-$24,999",
            "$25,000-$99,999",
            "$100,000+",
          ]}
        />

        <MyDropdown
          name="Audience Location"
          valueId="location"
          options={[
            "north_america",
            "south_america",
            "western_europe",
            "eastern_europe",
            "middle_east",
            "africa",
            "south_asia",
            "east_asia",
          ]}
        />

        {isSaving && (
          <div className="text-center">
            <FontAwesomeIcon icon={faSpinner} spin />
          </div>
        )}
        <SaveButton isSaving={isSaving} />
        {(props.isEditingAccount || isCreatingAnExampleCompany) && (
          <CancelButton onCancel={props.onCancel} />
        )}
        {props.isEditingAccount && !isCreatingAnExampleCompany && (
          <Button
            className="delete-button"
            variant="danger"
            onClick={(event) => {
              event.preventDefault();
              setShowDeleteModal(true);
            }}
          >
            Delete all data for this account
          </Button>
        )}
      </div>
      <Modal
        show={showDeleteModal}
        onHide={() => setShowDeleteModal(false)}
        animation={true}
      >
        <Modal.Header closeButton>
          <Modal.Title>Confirm Deletion</Modal.Title>
        </Modal.Header>

        <Modal.Body>
          <p>
            Are you sure you would like to remove all data about this account?
          </p>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Go Back
          </Button>
          <Button
            variant="danger"
            onClick={() => {
              myFetch
                .post("/user/delete_account", {
                  account_id: selectedCompany.account_id,
                })
                .then((response) => response.json())
                .then((data) => {
                  if (data.success) {
                    window.location.reload();
                  }
                });
            }}
          >
            Delete Account
          </Button>
        </Modal.Footer>
      </Modal>
    </MyForm>
  );
};

const FormItem = (props) => {
  return (
    <Form.Group>
      <Form.Label className="form-label text-right">{props.name}</Form.Label>
      {props.children || (
        <Form.Control plaintext readOnly defaultValue={props.defaultValue} />
      )}
    </Form.Group>
  );
};

export const SaveButton = (props) => {
  return (
    <Form.Group>
      <Button className="save-button" disabled={props.isSaving} type="submit">
        {props.text || "Save"}
      </Button>
      <br />
      {props.saved && <span className="success">Saved</span>}
    </Form.Group>
  );
};

export const CancelButton = (props) => {
  return (
    <Form.Group>
      <Button
        className="cancel-button"
        disabled={props.isSaving}
        onClick={props.onCancel}
      >
        {props.text || "Cancel"}
      </Button>
    </Form.Group>
  );
};

export const MyForm = (props) => {
  return (
    <Form
      style={{ maxWidth: 800 }}
      className="text-left"
      onSubmit={(event) => {
        event.preventDefault();
        event.stopPropagation();
        props.onSubmit(event);
      }}
    >
      <h2>{props.title}</h2>
      {props.children}
    </Form>
  );
};
