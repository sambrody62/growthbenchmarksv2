import React, { useMemo } from "react";
import { useHistory } from "react-router-dom";
import { Container, Nav, Navbar, Form, Image } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner } from "@fortawesome/fontawesome-free-solid";
import Select from "react-select";
import moment from "moment";

import { Logout } from "./Logout";
import { dot } from "./dot";
import {
  GOOGLE_PROVIDER,
  GOOGLE_FAKE_PROVIDER,
  FACEBOOK_PROVIDER,
  FACEBOOK_FAKE_PROVIDER,
} from "./providers";

export const Navigation = (props) => {
  const history = useHistory();
  const {
    user,
    isLoading,
    isLoadingCompanies,
    selectedCompany,
    companiesList = [],
    handleSelectCompany,
    onLogout,
  } = props;
  const today = moment().format("YYYY-MM-DD");

  const myCompanyOptions = useMemo(() => {
    const googleOptions = [];
    const googleFakeOptions = [];
    const facebookOptions = [];
    const facebookFakeOptions = [];

    for (let i = 0; i < companiesList.length; i++) {
      const company = companiesList[i];
      switch (company.provider_id) {
        case GOOGLE_PROVIDER:
          googleOptions.push(company);
          break;
        case GOOGLE_FAKE_PROVIDER:
          googleFakeOptions.push(company);
          break;
        case FACEBOOK_PROVIDER:
          facebookOptions.push(company);
          break;
        case FACEBOOK_FAKE_PROVIDER:
          facebookFakeOptions.push(company);
          break;
      }
    }
    return [
      { label: "Facebook", options: sortAndMap(facebookOptions) },
      { label: "Google", options: sortAndMap(googleOptions) },
      {
        label: "Facebook Example Companies",
        options: sortAndMap(facebookFakeOptions),
      },
      {
        label: "Google Example Comapnies",
        options: sortAndMap(googleFakeOptions),
      },
    ];
  }, [companiesList]);

  function sortAndMap(listOfCompanies) {
    return listOfCompanies
      .sort((companyA, companyB) => {
        return (companyA && companyA.name && companyA.name.toLowerCase()) >
          companyB?.name?.toLowerCase()
          ? 1
          : -1;
      })
      .map((company) => {
        return {
          value: company?.account_id,
          label: `${company.name || company.account_id} ${
            company?.isExampleCompany ? "" : `(${company?.account_id})`
          }`,
          last_date_saved: company?.last_date_saved,
          isExampleCompany: company?.isExampleCompany,
          has_completed_questionnaire: company?.has_completed_questionnaire,
        };
      });
  }

  return (
    <div style={{ backgroundColor: "white" }}>
      <Container>
        <Navbar>
          <Navbar.Brand className="m-0">
            <Image
              fluid
              onClick={() => history.push("/")}
              src="/images/Logo.png"
              style={{ cursor: "pointer", maxHeight: 60 }}
              alt="Logo"
            />
          </Navbar.Brand>
          {isLoadingCompanies ? (
            <h2 className="m-auto pl-0 pr-3 text-center">
              Loading Companies...
              <FontAwesomeIcon
                style={{
                  fontSize: 20,
                  marginLeft: 10,
                }}
                icon={faSpinner}
                spin
              />
            </h2>
          ) : (
            <Form.Group
              className="m-auto p-3"
              style={{ width: "100%", maxWidth: "400px" }}
            >
              {companiesList && companiesList.length > 0 && (
                <>
                  <Form.Label
                    style={{
                      textTransform: "uppercase",
                      letterSpacing: "0.2em",
                    }}
                  >
                    Ad Account
                  </Form.Label>{" "}
                  <Select
                    onChange={({ value: selectedCompanyId }) => {
                      handleSelectCompany(selectedCompanyId);
                    }}
                    value={{
                      value: selectedCompany?.account_id,
                      label: `${
                        selectedCompany.name || selectedCompany.account_id
                      } ${
                        selectedCompany?.isExampleCompany
                          ? ""
                          : `(${selectedCompany?.account_id})`
                      }`,
                      last_date_saved: selectedCompany?.last_date_saved,
                      has_completed_questionnaire:
                        selectedCompany?.has_completed_questionnaire,
                      isExampleCompany: selectedCompany?.isExampleCompany,
                    }}
                    styles={{
                      option: (styles, { data }) => {
                        return {
                          ...styles,
                          ...dot(
                            data?.isExampleCompany
                              ? "lightgreen"
                              : data.has_completed_questionnaire &&
                                data.last_date_saved
                              ? today === data.last_date_saved
                                ? "lightgreen"
                                : "yellow"
                              : "red"
                          ),
                        };
                      },
                    }}
                    options={myCompanyOptions}
                  />
                </>
              )}
            </Form.Group>
          )}
          <Nav style={{ minInlineSize: "fit-content" }}>
            <Logout
              user={user}
              isLoading={isLoading}
              onLogout={() => onLogout()}
            />
          </Nav>
        </Navbar>
      </Container>
    </div>
  );
};
