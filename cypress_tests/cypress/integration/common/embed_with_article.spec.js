describe("Tests for embedded poll, survey, and quiz", () => {
    const url = "/en/sections/questionnaire-testing/article-with-poll-survey-and-quiz/";

    it("Visits the article page", () => {
        cy.visitUrl(url);
        cy.testTitle("Article with poll, survey, and quiz", ".article__content>h1");

        cy.get("[id=id_poll_radio_1]").check()
        cy.submit(".poll-page__btns>.survey-page__btn", "Submit");
        cy.submit(".icon-btn__title", "Back")

        cy.submit(".survey-page__btn", "Log in to participate");
        cy.login("saqlain", "saqlain");
        cy.get(".survey-page__content>div>label>input").check();
        cy.submit(".survey-page__btn", "Submit")
        cy.visitUrl(url);

        cy.get(".quiz-page__content>div>label>input").check();
        cy.submit(".quiz-page__btns>.survey-page__btn", "Submit");
    });

});
