# HACKATHON CHATGPT

Members: \
1.Chong Pohyi\
2.Teo Zheng Xi\
3.Teoh Xi Xian\
4.Tan Wei Feng\
5.Lim Jie Shin


In Peninsular Malaysia, floods happen almost every year. Having a Chat AI to answer questions regarding floods will be definately helpful.
**📖 Overview**

This project is a Flood Safety Assistant designed to support vulnerable communities in Malaysia during flood emergencies. It uses an embedded Large Language Model (LLM) to generate structured, empathetic responses based on user queries. The system prioritizes accessibility, safety, and clarity — especially for elderly, OKU, infants, and pets.
**Core Capabilities**
**Intelligent Family-First Routing:** Recommends the safest PPS (Public Protection Shelter) based on accessibility and risk.

**Accessibility & Pet Support:** Flags PPS features like wheelchair access, OKU toilets, ramps, and pet policies.

**Rumour Verification: Confirms or denies rumours** (e.g. PPS closure, electricity cut-off) using trusted sources.

**Structured Output:** Every response includes:

**Recommendation

**Accessibility & Pets

**Rationale (why other PPS options were rejected)


**SmartPPS: BANTU BANJIR** is here to help to encounter issues and questions regarding floods.

## DATA SET
Due to time limit and avoiding copyright issues for scraping government data, we use a set of mock data for our AI to run.

## JAMAIBASE
**Rumours detector

**All structured responses are managed in Jama Connect under tables like english_prompt and malay_prompt.**

Table Columns:
Column	Description
Name	Scenario or query type (e.g. “public transport”, “OKU access”)
Recommendation	Safest PPS or action to take
Accessibility & Pet	Accessibility features and pet policy (e.g. “Mesra kerusi roda, haiwan dibenarkan”)
Rationale	3-point explanation of rejected PPS options
Answer_Queries	Notes on how the assistant should respond to user queries

**Usage:**
Input queries are stored in Name or Answer_Queries.

LLM generates structured outputs for each row.

Backend engineers consume Jama entries as JSON for UI rendering.

All entries are bilingual (English & Bahasa Melayu) and follow strict formatting rules.

## BACKEND

## FRONTEND

## AUTHORS

- [@iztzx](https://github.com/iztzx)
- [@JieShin27](https://github.com/JieShin27)
- [@Pohyi118](https://github.com/Pohyi118)
- [@TeohXiXian-2025](https://github.com/TeohXiXian-2025)
- [@TWF06](https://github.com/TWF06)

## SLIDE AND DEMO

https://www.canva.com/design/DAG5rgvK9O0/sVuH6uLgxUhIjR6qDCZqWQ/view

