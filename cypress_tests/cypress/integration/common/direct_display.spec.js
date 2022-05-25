describe("Direct display tests for all types", () => {
    const url = "/en/sections/questionnaire-testing/";
    const titles = [
        {
            "selector": ".title.polls-widget__title",
            "text": "Poll multiline field"
        },
        {
            "selector": ".title.survey-page__title",
            "text": "Survey with optional checkbox"
        },
        {
            "selector": ".title.quiz-page__title",
            "text": "Quiz with checkbox"
        }
    ];

    it("Visits the site questionnaires page", () => {
        cy.visitUrl(url);
        titles.forEach(title => {
            cy.testTitle(title.text, title.selector);
        });

        //cy.get(".quest-item__number").contains("1 of 1 question");

        cy.get("[id=id_poll_multiline]").type("Example text test");
        cy.submit(".poll-page__btns>.survey-page__btn", "Submit");
        cy.submit(".icon-btn__title", "Back");

        cy.get("[name=text_field]").type("test");
        cy.submit(".survey-page__btn", "Next");
        cy.visitUrl(url);

        cy.get(".quiz-page__content>div>label>input").check();
        cy.submit(".quiz-page__btns>.survey-page__btn", "Submit");
    });

});
