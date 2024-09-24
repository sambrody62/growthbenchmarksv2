import React from "react";
import { Link } from "react-router-dom";
import { Row, Col, Image, Container } from "react-bootstrap";

import { filters } from "./filters";

export const Footer = () => {
  return (
    <footer>
      <Container>
        <Row>
          <Col xs={12} md={3} className="navigationFooter">
            <h6 className="footer-title">Navigation</h6>
            <Link to="/">Home</Link>
            <br />
            <Link to="/about">About</Link>
            <br />
            <a
              target="_blank"
              rel="noreferrer"
              href="https://try.ladder.io/terms-of-service/"
            >
              Terms
            </a>
            <br />
            <a
              target="_blank"
              rel="noreferrer"
              href="https://try.ladder.io/privacypolicy/"
            >
              Privacy
            </a>
          </Col>

          <Col xs={12} md={6}>
            <h6 className="footer-title">Performance Benchmarks</h6>
            <Row>
              <Col xs={12} md={6} className="text-right text-center-xs">
                {Object.keys(filters).map((filterKey, index) => {
                  if (index <= 3) {
                    return (
                      <span
                        key={filterKey}
                        id={"col-" + Math.ceil(index / 3.0 - 0.1)}
                      >
                        <Link to={`/facebook/${filterKey}/all_companies`}>
                          Facebook Ads {filterKey.toUpperCase()}
                        </Link>
                        {index < Object.keys(filters).length - 1 && <br />}
                      </span>
                    );
                  }
                })}
              </Col>
              <Col xs={12} md={6} className="text-left text-center-xs">
                {Object.keys(filters).map((filterKey, index) => {
                  if (index >= 3) {
                    return (
                      <span
                        key={filterKey}
                        id={"col-" + Math.ceil(index / 3.0 - 0.1)}
                      >
                        <Link to={`/facebook/${filterKey}/all_companies`}>
                          Facebook Ads {filterKey.toUpperCase()}
                        </Link>
                        {index < Object.keys(filters).length - 1 && <br />}
                      </span>
                    );
                  }
                })}
              </Col>
            </Row>
          </Col>
          <Col xs={12} md={3}>
            <a target="_blank" rel="noreferrer" href="https://ladder.io/">
              <Image
                fluid
                src="/images/Ladder_Logo_Black.png"
                style={{ maxHeight: 20 }}
              />
            </a>

            <br />
            <p style={{ marginTop: "10px" }}>
              Created by Ladder &copy; {new Date().getFullYear()}
            </p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};
