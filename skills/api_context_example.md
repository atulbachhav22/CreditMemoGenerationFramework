# Skill Name: API Context Demo - User & Post Analysis

## Metadata
- Version: 1.0.0
- Author: SkillEngine Team
- Description: Demonstrates API Context feature by fetching data from JSONPlaceholder API and analyzing it
- Tags: demo, api-context, analysis

## Context
This skill demonstrates the API Context feature of SkillEngine. It fetches user and post data
from the public JSONPlaceholder API (https://jsonplaceholder.typicode.com) and performs
analysis on the retrieved data. No authentication is required.

## API Context

### API: user_profile
- Endpoint: https://jsonplaceholder.typicode.com/users/1
- Method: GET
- Description: Fetches user profile data including name, email, company, and address

### API: user_posts
- Endpoint: https://jsonplaceholder.typicode.com/posts
- Method: GET
- Query Params: userId=1
- Description: Fetches all posts authored by the user

## Steps

### Step 1: Analyze User Profile
**Instruction:**
Using the user profile data provided in the API Context Data (alias: user_profile),
create a structured summary of the user including:

1. Full name and username
2. Contact information (email, phone, website)
3. Address (formatted as a single line)
4. Company name and catch phrase

Format the output as a clean, readable profile card.

**Expected Output:**
A formatted user profile summary with all key fields clearly labeled.

**Verification:**
- Must contain the user's full name
- Must contain the user's email address
- Must contain company information

---

### Step 2: Analyze Post Content
**Instruction:**
Using the user's posts data provided in the API Context Data (alias: user_posts),
analyze the posts and provide:

1. Total number of posts
2. Average title length (in words)
3. A brief summary of the top 3 posts (by title)
4. Common themes or topics across the posts

**Expected Output:**
A structured analysis of the user's posting activity with statistics and content summary.

**Verification:**
- Must include the total post count
- Must include summaries of at least 3 posts

---

### Step 3: Generate Combined Report
**Instruction:**
Using the user profile analysis from Step 1 and the post content analysis from Step 2,
generate a combined user activity report that includes:

1. User Profile Summary (from Step 1)
2. Content Activity Summary (from Step 2)
3. An overall assessment of the user's activity level and content focus

**API Context:**
- Endpoint: https://jsonplaceholder.typicode.com/comments
- Method: GET
- Query Params: postId=1
- Extract: $.0
- Alias: sample_comment

Include information about community engagement using the sample comment data.

**Expected Output:**
A comprehensive user activity report combining profile data, content analysis,
and engagement insights.

**Verification:**
- Must contain both profile and content sections
- Must include an overall assessment

---

## Final Output Format
A comprehensive user activity report with three sections:
1. User Profile
2. Content Activity
3. Overall Assessment with engagement insights

## Success Criteria
- All API data successfully retrieved and incorporated
- User profile accurately summarized
- Post content meaningfully analyzed
- Combined report is coherent and well-structured
