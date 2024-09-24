import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Route,
  Switch,
  Redirect,
} from "react-router-dom";

import { firebase } from "./Components/Firebase";
import { Main } from "./Components/Main";
import { Benchmark } from "./Components/Benchmark";
import { BenchmarksList } from "./Components/BenchmarksList";
import { About } from "./Components/static/Static";
import { Insights } from "./Components/Insights";
import { Profile } from "./Components/Profile";
import { NotFound } from "./Components/NotFound";
import { EmailLogin } from "./Components/EmailLogin";

import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

function App() {
  const [user, setUser] = useState();

  const logout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("selectedCompany");
    localStorage.removeItem("cache");
  };

  firebase.auth().onAuthStateChanged(() => {
    const firebaseUser = firebase.auth().currentUser;
    setUser(firebaseUser);
  });

  useEffect(() => {
    try {
      const authUser = JSON.parse(localStorage.getItem("user"));
      if (authUser) {
        setUser(authUser);
      }
    } catch (e) {
      console.log("There was an error loading the data/user: " + e);
    }
  }, []);

  return (
    <Router>
      <Switch>
        <Route path="/about" exact component={About} />
        <Route
          path="/logout"
          exact
          render={() => {
            logout();
            return <Redirect to="/" />;
          }}
        />
        <Route path="/join" exact component={EmailLogin} />
        <Route
          path="/profile"
          exact
          render={(props) => {
            return <Profile {...props} user={user} />;
          }}
        />
        <Route path="/:providerName/insights" exact component={Insights} />
        <Route
          path="/privacy"
          exact
          component={() => {
            window.location.href = "https://try.ladder.io/privacypolicy/";
            return null;
          }}
        />
        <Route
          path="/terms"
          exact
          component={() => {
            window.location.href = "https://try.ladder.io/terms-of-service/";
            return null;
          }}
        />

        <Route
          path="/:providerName/benchmarks"
          exact
          component={BenchmarksList}
        />

        <Route
          path={["/", "/:selectedCompanyId/:selectedFilterId"]}
          exact
          render={(props) => {
            return (
              <Main {...props} user={user} setUser={setUser} logout={logout} />
            );
          }}
        />

        <Route
          path="/embed/:providerName/:metricName/:benchmarkName"
          exact
          render={(props) => {
            return <Benchmark {...props} embedded />;
          }}
        />
        <Route
          path={[
            "/:providerName/:metricName/:benchmarkName",
            "/:providerName/:metricName/:benchmarkPrefixName/:benchmarkSuffixName",
          ]}
          exact
          component={Benchmark}
        />
        <Route path="*" component={NotFound} />
      </Switch>
    </Router>
  );
}

export default App;
