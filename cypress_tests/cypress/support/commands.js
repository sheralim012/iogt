// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
Cypress.Commands.add('login', (username, password) => {
    cy.get('[name=login]').type(username);
    cy.get('[name=password]').type(password);
    cy.get('.profile-form__btn>span').contains("Log in").click();
});

Cypress.Commands.add('adminLogin', (username, password) => {
    cy.get('[name=username]').type(username);
    cy.get('[name=password]').type(password);
    cy.get('.button.button-longrunning>em').contains("Sign in").click();
});

Cypress.Commands.add("visitUrl", (url) => {
    cy.visit(url);
    cy.url().should("include", url);
});

Cypress.Commands.add("testTitle", (text, selector) => {
    cy.get(selector)
        .contains(text)
        .should("be.visible");
});

Cypress.Commands.add("testDescription", (text, selector) => {
    cy.get(selector)
        .contains(text)
        .should("be.visible");
});

Cypress.Commands.add("submit", (selector, text) => {
    cy.get(selector)
        .contains(text)
        .should("be.visible")
        .click();
});

Cypress.Commands.add("thanksText", (selector, text) => {
    cy.get(selector)
        .contains(text)
        .should("be.visible");
});

Cypress.Commands.add("testQuestions", (selector) => {
    let questionNumbers = []

    cy.get(selector).each(($el, index) => {
        questionNumbers.push($el)
    });
    cy.get(selector).each(($el, index) => {
        cy.wrap($el)
            .should("be.visible")
            .contains(
                `${index + 1} of ${questionNumbers.length} ${questionNumbers.length === 1 ? "question" : "questions"}`
            )
    });
});

Cypress.Commands.add("checkPollResults", ($selector) => {
    cy.get($selector).each(($el) => {
        cy.wrap($el)
            .should("be.visible")
            .contains(/\\d+(?:d+)?|%/);
    });
})
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
