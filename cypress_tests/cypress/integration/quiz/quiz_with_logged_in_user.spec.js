describe("Quiz with logged in user tests", () => {
    const url = "/en/sections/questionnaire-testing/sample-quiz/";

    it("Checks for the login button and logs in the user", () => {
        cy.visitUrl(url);
        cy.submit(".survey-page__btn", "Log in to participate");
        cy.login("saqlain", "saqlain");
    });

    it("visits the quiz page", () => {
        cy.get(".quest-item__step-desc>span").contains("Select one");
        cy.get(".quest-item__step-desc>span").contains("Select one");
    });

    it("Selects the answers and submit them", () => {
        cy.get("[id=id_radio_button_question_0]").click();
        cy.get("select").select("c2");

        cy.submit("button[type=submit]>span", "Submit");
        cy.url().should("include", `/?back_url=${url}&form_length=2`);
    });
});