import React from "react";
import { Link } from "react-router-dom";

import { Navigation } from "./Navigation";
import { Footer } from "./Footer";

export const NotFound = () => {
  return (
    <>
      <Navigation />
      <div
        className="ml-auto mr-auto mt-5 main-content text-center"
        style={{ flex: "1 0 auto", maxWidth: 1000 }}
      >
        <h1 className="text-center">Page Not Found</h1>
        <p>
          Click <Link to="/">here</Link> to go home!
        </p>
      </div>
      <Footer />
    </>
  );
};
