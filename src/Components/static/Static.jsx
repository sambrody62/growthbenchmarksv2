/* eslint react/no-unescaped-entities: 0 */
import React from "react";
import { Container } from "react-bootstrap";

import { Navigation } from "../Navigation";
import { Footer } from "../Footer";

export const About = () => {
  return (
    <>
      <Navigation />
      <Container className="mt-5 d-flex flex-column" style={{ flex: 1 }}>
        <h1>About Us</h1>
        <div style={{ fontWeight: "normal" }}>
          <p>
            What does good performance look like? With thousands of factors
            affecting your results, unpredictable macro and micro events and
            regular algorithm changes, it can be hard to prove you're doing a
            good job on marketing. We built Growth Benchmarks to give you
            reliable metric benchmarks, so you know if your campaigns are
            driving above average returns (or not).
          </p>
          <p>
            Based on how you answer the questionnaire on signup, we pair you
            with 5 companies that have similar attributes that already exist in
            the database. This 'similar companies' index gives you a real time
            understanding of if the dips and spikes you're seeing in your
            numbers are something you did or just changes in the market. You can
            also compare against all companies in our collection using Growth
            Benchmarks.
          </p>
          <p>
            Connecting your Facebook account will provide us your email address,
            name and a list of your ad accounts. We will not pull or store
            performance data until you fill in the onboarding form for a
            specific account. We will never sell or share your individual
            account data with partners, we only use it to provide aggregate
            benchmarks (
            <u>
              <i>anonymously</i>
            </u>
            ).
          </p>
          <p>
            The Growth Benchmarks platform was built by{" "}
            <a href="https://ladder.io/" target="_blank" rel="noreferrer">
              Ladder
            </a>{" "}
            as part of our mission to take the guesswork out of growth. Ladder
            strategists have the exact same level of access as you get by
            signing up for free. We don't have any plans to charge for Growth
            Benchmarks, but we do plan to link out to the{" "}
            <a href="https://ladder.io/" target="_blank" rel="noreferrer">
              Ladder
            </a>{" "}
            website where it would be mutually beneficial to do so.
          </p>
        </div>
      </Container>
      <Footer />
    </>
  );
};
