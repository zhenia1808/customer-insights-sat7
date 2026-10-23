# Security

## What this project does

This is a local demonstration tool. It counts cancellations, looks for themes in customer comments, and can use a model to flag active customers who may need attention. The “post” is simulated: it saves the report to a local file instead of sending it to Slack.

## Risks and what was done

- **Database credentials:** Credential-like values were removed from the submitted project. We did not check whether they were valid or had been used. The project uses SQLite, which does not need a separate database username or password.

- **Unsafe database searches:** Putting a country name directly into a database search can let the search be changed in an unsafe way. The staging code now passes the country name safely as a separate value.

- **Customer information in reports:** Reports may contain names, email addresses, and phone numbers. The “post” script saves the report locally; it does not send it to an outside service. Each run adds another entry to the channel log, so older reports stay there too. Review the log before sharing it.

- **Accidentally sharing local files:** Git is set to ignore database files, model files, reports, logs, environment files, and other generated files. This helps keep them out of a shared copy of the project. It does not erase files already committed or remove them from Git history.

- **Accidentally overwriting sample data:** The project uses fictional sample data for normal development and testing. Its database generator refuses to replace a database that already exists, which helps protect data from accidental loss.

- **Using customer data:** The model run used the local customer database provided with the project. Reports made from customer data may include identifying details, so keep them private and check them before sharing.

- **Model limits:** The training script compares Logistic Regression, Random Forest, and XGBoost, then chooses the model with the best average recall in cross-validation. Recall measures how many customers who cancelled the model catches. Results from one held-out evaluation may not carry over to other data. The model estimates general cancellation risk; it cannot predict who will cancel in a particular week. Do not use its list by itself to decide whom to contact.

- **Unsafe model files:** A saved model is loaded with `joblib`. A model file from an unknown source could run unsafe code when loaded, so only use a model you created or reviewed. Predictions are skipped unless a model is deliberately configured.

- **AI agent access:** `CLAUDE.md` tells Claude Code to use fictional data by default, keep customer details and secrets out of replies, logs, tests, and commits, and get approval before using real data or outside services. The project settings also block Claude Code’s file tools from opening or editing databases, reports, model files, and environment files. They block MCP tools, turn off bypass-permissions mode, and ask before certain actions such as installing packages or using selected network and publishing commands. These rules lower the chance of accidental access or sharing, but they are not a complete security barrier. They have not yet been checked in a Claude Code session.

- **Starter plugin hook:** The starter copy included a startup hook that tried to download and run code from the internet and send the `.env` file to a web address. That hook is not included in the submitted project. Leaving it out avoids running downloaded code or exposing environment settings when a session starts.

## What still needs care

Keep customer data and reports private, and review files before sharing the project. Store credentials outside the repository. If any removed value might belong to a real account, the account owner should change it.

The Claude Code settings do not block every possible way a program could access files or the internet. Before using this with real work, review who can access the data, how long it is kept, the model’s usefulness, the extra model packages, and the Claude Code settings. The model’s test results do not promise that it will work well for future customers.
