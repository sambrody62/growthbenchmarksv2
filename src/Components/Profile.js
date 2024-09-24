import React, { useState, useEffect } from "react";
import { Container, Col, Row } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner, faAngleLeft } from "@fortawesome/fontawesome-free-solid";
import Switch from "react-switch";
import { useHistory } from "react-router-dom";

import myFetch from "./myFetch";
import { firebase } from "./Firebase";

export const Profile = ({ user }) => {
  const history = useHistory();

  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(async () => {
    if (firebase.auth().currentUser) {
      // Go and get the subscribed status
      const { is_subscribed = false } = await myFetch
        .get("/user/get_is_subscribed")
        .then((response) => response.json());
      setIsSubscribed(is_subscribed || false);
      setIsLoading(false);
    }
  }, [user]);

  useEffect(() => {}, [user]);

  const handleUpdateIsSubscribed = async (updatedIsSubscribed) => {
    setIsSaving(true);
    await myFetch.post(`/user/update_is_subscribed`, {
      is_subscribed: updatedIsSubscribed,
    });
    setIsSubscribed(updatedIsSubscribed);
    setIsSaving(false);
  };

  if (!user) {
    return <h1>No user yet!</h1>;
  }

  return (
    <Container className="p-4">
      <h3 className="pb-5">Profile</h3>

      <Row>
        <Col md={6}>
          {isLoading ? (
            <div>
              <p>
                <span>
                  <FontAwesomeIcon icon={faSpinner} spin />
                </span>{" "}
                Loading....
              </p>
            </div>
          ) : (
            <div>
              <div className="mb-4">
                <a href="#" onClick={() => history.goBack()}>
                  <FontAwesomeIcon icon={faAngleLeft} />
                  <span className="pl-2">Go back</span>
                </a>
              </div>
              <div className="d-flex align-items-center">
                <span className="pr-2">Subscribe to emails:</span>
                <Switch
                  onChange={() => handleUpdateIsSubscribed(!isSubscribed)}
                  checked={isSubscribed}
                  uncheckedIcon={false}
                  checkedIcon={false}
                  onColor={"#804EEC"}
                  handleDiameter={18}
                  height={20}
                  width={40}
                  disabled={isSaving}
                />
              </div>
            </div>
          )}
        </Col>
      </Row>
    </Container>
  );
};
