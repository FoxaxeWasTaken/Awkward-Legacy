#!/bin/bash

# Generate a realistic 5-generation family tree
# The Smith Family Tree

API_URL="http://localhost:8000/api/v1"

echo "🌳 Generating 5-Generation Smith Family Tree..."
echo ""

# Helper function to create a person
create_person() {
    local first_name="$1"
    local last_name="$2"
    local sex="$3"
    local birth_date="$4"
    local death_date="$5"
    local birth_place="$6"
    local occupation="$7"
    local notes="$8"
    
    local data="{\"first_name\":\"$first_name\",\"last_name\":\"$last_name\",\"sex\":\"$sex\",\"birth_date\":\"$birth_date\""
    
    if [ -n "$death_date" ]; then
        data="$data,\"death_date\":\"$death_date\""
    fi
    
    if [ -n "$birth_place" ]; then
        data="$data,\"birth_place\":\"$birth_place\""
    fi
    
    if [ -n "$occupation" ]; then
        data="$data,\"occupation\":\"$occupation\""
    fi
    
    if [ -n "$notes" ]; then
        # Escape quotes in notes for JSON
        local escaped_notes=$(echo "$notes" | sed 's/"/\\"/g')
        data="$data,\"notes\":\"$escaped_notes\""
    fi
    
    data="$data}"
    
    local response=$(curl -s -X POST "$API_URL/persons/" \
        -H "Content-Type: application/json" \
        -d "$data")
    
    echo "$response" | jq -r '.id'
}

# Helper function to create a family
create_family() {
    local husband_id="$1"
    local wife_id="$2"
    local marriage_date="$3"
    local marriage_place="$4"
    
    local data="{\"husband_id\":\"$husband_id\",\"wife_id\":\"$wife_id\""
    
    if [ -n "$marriage_date" ]; then
        data="$data,\"marriage_date\":\"$marriage_date\""
    fi
    
    if [ -n "$marriage_place" ]; then
        data="$data,\"marriage_place\":\"$marriage_place\""
    fi
    
    data="$data}"
    
    local response=$(curl -s -X POST "$API_URL/families/" \
        -H "Content-Type: application/json" \
        -d "$data")
    
    echo "$response" | jq -r '.id'
}

# Helper function to add a child to a family
add_child() {
    local family_id="$1"
    local child_id="$2"
    
    curl -s -X POST "$API_URL/children/" \
        -H "Content-Type: application/json" \
        -d "{\"family_id\":\"$family_id\",\"child_id\":\"$child_id\"}" > /dev/null
}

# Helper function to create an event
create_event() {
    local family_id="$1"
    local person_id="$2"
    local event_type="$3"
    local event_date="$4"
    local event_place="$5"
    local event_description="$6"
    
    local data="{\"type\":\"$event_type\""
    
    if [ -n "$family_id" ]; then
        data="$data,\"family_id\":\"$family_id\""
    fi
    
    if [ -n "$person_id" ]; then
        data="$data,\"person_id\":\"$person_id\""
    fi
    
    if [ -n "$event_date" ]; then
        data="$data,\"date\":\"$event_date\""
    fi
    
    if [ -n "$event_place" ]; then
        data="$data,\"place\":\"$event_place\""
    fi
    
    if [ -n "$event_description" ]; then
        # Escape quotes in description for JSON
        local escaped_description=$(echo "$event_description" | sed 's/"/\\"/g')
        data="$data,\"description\":\"$escaped_description\""
    fi
    
    data="$data}"
    
    curl -s -X POST "$API_URL/events/" \
        -H "Content-Type: application/json" \
        -d "$data" > /dev/null
}

echo "📅 GENERATION 1 (1920s) - The Founders"
echo "Creating William and Margaret Smith..."
william_id=$(create_person "William" "Smith" "M" "1920-03-15" "1995-12-10" "Boston, MA" "Carpenter" "Served in World War II as a combat engineer. Founded Smith Construction Company in 1950. Known for his integrity and craftsmanship.")
margaret_id=$(create_person "Margaret" "Brown" "F" "1922-07-22" "2000-05-18" "Boston, MA" "Homemaker" "Active in the local church community. Volunteered at the Boston Public Library for 30 years. Excellent cook, famous for her apple pies.")
gen1_family=$(create_family "$william_id" "$margaret_id" "1941-06-14" "Boston, MA")
echo "✓ William & Margaret Smith family created"
echo ""

echo "📅 GENERATION 2 (1940s-1950s) - The Children"
# William and Margaret have 4 children
echo "Creating children of William & Margaret..."
james_id=$(create_person "James" "Smith" "M" "1942-04-10" "" "Boston, MA" "Lawyer" "Harvard Law School graduate. Specialized in civil rights law. Partner at Smith & Associates. Argued before the Supreme Court twice.")
robert_id=$(create_person "Robert" "Smith" "M" "1945-08-23" "" "Boston, MA" "Doctor" "Pediatrician at Boston Children's Hospital. Published research on childhood vaccines. Awarded the Humanitarian Award in 1998.")
mary_id=$(create_person "Mary" "Smith" "F" "1948-11-05" "" "Boston, MA" "Teacher" "Elementary school principal for 25 years. Introduced innovative music education programs. Passionate about children's literacy.")
elizabeth_id=$(create_person "Elizabeth" "Smith" "F" "1952-02-14" "" "Boston, MA" "Nurse" "Head nurse in the ICU at Massachusetts General Hospital. Mentored over 100 nursing students during her career.")

add_child "$gen1_family" "$james_id"
add_child "$gen1_family" "$robert_id"
add_child "$gen1_family" "$mary_id"
add_child "$gen1_family" "$elizabeth_id"
echo "✓ Added 4 children to Gen 1"

# Create spouses for Gen 2
echo "Creating spouses for Gen 2..."
jennifer_id=$(create_person "Jennifer" "Davis" "F" "1943-09-12" "" "New York, NY" "Accountant" "CPA with expertise in tax law. Helped establish the first women's professional networking group in Boston.")
linda_id=$(create_person "Linda" "Wilson" "F" "1946-12-30" "" "Philadelphia, PA" "Librarian" "Chief librarian at Boston Public Library. Digitized the historical archives. Passionate about preserving local history.")
michael_id=$(create_person "Michael" "Johnson" "M" "1947-05-18" "" "Chicago, IL" "Engineer" "Aerospace engineer who worked on the Space Shuttle program. Holds 12 patents in propulsion systems.")
david_id=$(create_person "David" "Martinez" "M" "1950-03-25" "" "San Francisco, CA" "Architect" "Designed several award-winning sustainable buildings. LEED certification expert. Loves modern minimalist design.")

# Create Gen 2 families
james_family=$(create_family "$james_id" "$jennifer_id" "1965-07-20" "Boston, MA")
robert_family=$(create_family "$robert_id" "$linda_id" "1970-09-15" "Boston, MA")
mary_family=$(create_family "$michael_id" "$mary_id" "1972-06-08" "Chicago, IL")
elizabeth_family=$(create_family "$david_id" "$elizabeth_id" "1975-04-12" "San Francisco, CA")
echo "✓ Created 4 Gen 2 families"

# Add divorce event to James & Jennifer (Gen 2) - they divorce after 20 years
create_event "$james_family" "" "divorce" "1985-06-15" "Boston, MA" "Divorce finalized after 20 years of marriage. Irreconcilable differences."
echo "✓ Added divorce event to James & Jennifer Smith"

# Add some marriage events to other couples for variety
create_event "$robert_family" "" "marriage" "1970-09-15" "Boston, MA" "Beautiful ceremony at Trinity Church in Boston."
create_event "$mary_family" "" "marriage" "1972-06-08" "Chicago, IL" "Wedding ceremony at the Chicago Cultural Center."
echo "✓ Added marriage events to Robert & Linda, Michael & Mary"

echo ""

echo "📅 GENERATION 3 (1960s-1980s) - The Grandchildren"
# James & Jennifer have 3 children
echo "Creating children of James & Jennifer..."
thomas_id=$(create_person "Thomas" "Smith" "M" "1966-10-15" "" "Boston, MA" "Software Engineer" "Early internet pioneer. Co-founded a successful tech startup in the 1990s. Enjoys sailing and photography.")
sarah_id=$(create_person "Sarah" "Smith" "F" "1968-12-22" "" "Boston, MA" "Marketing Manager")
daniel_id=$(create_person "Daniel" "Smith" "M" "1971-03-30" "" "Boston, MA" "Dentist" "Runs a family dental practice. Volunteers at free dental clinics. Marathon runner who completed Boston Marathon 10 times.")

add_child "$james_family" "$thomas_id"
add_child "$james_family" "$sarah_id"
add_child "$james_family" "$daniel_id"

# Robert & Linda have 2 children
echo "Creating children of Robert & Linda..."
jennifer2_id=$(create_person "Jennifer" "Smith" "F" "1971-05-18" "" "Boston, MA" "Physician")
christopher_id=$(create_person "Christopher" "Smith" "M" "1974-08-25" "" "Boston, MA" "Professor")

add_child "$robert_family" "$jennifer2_id"
add_child "$robert_family" "$christopher_id"

# Michael & Mary have 4 children
echo "Creating children of Michael & Mary..."
emily_id=$(create_person "Emily" "Johnson" "F" "1973-07-12" "" "Chicago, IL" "Artist" "Contemporary painter whose work has been exhibited in galleries across the US. Inspired by nature and urban landscapes.")
matthew_id=$(create_person "Matthew" "Johnson" "M" "1975-09-20" "" "Chicago, IL" "Journalist")
jessica_id=$(create_person "Jessica" "Johnson" "F" "1978-11-08" "" "Chicago, IL" "Chef" "Award-winning chef and restaurateur. Appeared on several cooking shows. Specializes in farm-to-table cuisine.")
andrew_id=$(create_person "Andrew" "Johnson" "M" "1981-01-15" "" "Chicago, IL" "Musician" "Professional jazz pianist. Released three albums. Teaches music at the Chicago Conservatory.")

add_child "$mary_family" "$emily_id"
add_child "$mary_family" "$matthew_id"
add_child "$mary_family" "$jessica_id"
add_child "$mary_family" "$andrew_id"

# David & Elizabeth have 3 children
echo "Creating children of David & Elizabeth..."
sophia_id=$(create_person "Sophia" "Martinez" "F" "1976-04-22" "" "San Francisco, CA" "Designer" "UX/UI designer for major tech companies. Advocates for accessible design. Loves hiking in the Sierras.")
alexander_id=$(create_person "Alexander" "Martinez" "M" "1979-06-30" "" "San Francisco, CA" "Entrepreneur" "Founded a renewable energy startup. TED speaker on sustainable technology. Angel investor in green tech companies.")
olivia_id=$(create_person "Olivia" "Martinez" "F" "1982-12-18" "" "San Francisco, CA" "Veterinarian")

add_child "$elizabeth_family" "$sophia_id"
add_child "$elizabeth_family" "$alexander_id"
add_child "$elizabeth_family" "$olivia_id"
echo "✓ Added 12 children to Gen 2 (total Gen 3)"

# Create spouses for Gen 3
echo "Creating spouses for Gen 3..."
amanda_id=$(create_person "Amanda" "Taylor" "F" "1967-08-10" "" "Boston, MA" "Project Manager")
kevin_id=$(create_person "Kevin" "Anderson" "M" "1968-11-15" "" "New York, NY" "Consultant")
lisa_id=$(create_person "Lisa" "Thomas" "F" "1970-05-20" "" "Boston, MA" "Pharmacist")
brian_id=$(create_person "Brian" "Harris" "M" "1970-09-08" "" "Seattle, WA" "Data Scientist")
rachel_id=$(create_person "Rachel" "White" "F" "1974-02-14" "" "Portland, OR" "Psychologist")
mark_id=$(create_person "Mark" "Clark" "M" "1973-06-25" "" "Austin, TX" "Financial Advisor")
ashley_id=$(create_person "Ashley" "Lewis" "F" "1976-10-30" "" "Denver, CO" "HR Manager")
ryan_id=$(create_person "Ryan" "Walker" "M" "1978-12-05" "" "Miami, FL" "Real Estate Agent")
nicole_id=$(create_person "Nicole" "Hall" "F" "1980-03-18" "" "Atlanta, GA" "Event Planner")
jason_id=$(create_person "Jason" "Young" "M" "1975-07-22" "" "Los Angeles, CA" "Film Producer")
melissa_id=$(create_person "Melissa" "King" "F" "1980-09-12" "" "San Diego, CA" "Interior Designer")
brandon_id=$(create_person "Brandon" "Wright" "M" "1981-11-28" "" "Phoenix, AZ" "Sales Director")

# Create Gen 3 families (8 families - not all Gen 3 members get married)
thomas_family=$(create_family "$thomas_id" "$amanda_id" "1990-08-15" "Boston, MA")
sarah_family=$(create_family "$kevin_id" "$sarah_id" "1992-06-20" "New York, NY")
daniel_family=$(create_family "$daniel_id" "$lisa_id" "1995-09-10" "Boston, MA")
jennifer2_family=$(create_family "$brian_id" "$jennifer2_id" "1996-05-25" "Seattle, WA")
christopher_family=$(create_family "$christopher_id" "$rachel_id" "1998-07-12" "Portland, OR")
emily_family=$(create_family "$mark_id" "$emily_id" "1997-04-18" "Austin, TX")
matthew_family=$(create_family "$matthew_id" "$ashley_id" "2000-10-22" "Denver, CO")
jessica_family=$(create_family "$ryan_id" "$jessica_id" "2002-03-30" "Miami, FL")
andrew_family=$(create_family "$andrew_id" "$nicole_id" "2005-08-14" "Atlanta, GA")
sophia_family=$(create_family "$jason_id" "$sophia_id" "1999-11-20" "Los Angeles, CA")
alexander_family=$(create_family "$alexander_id" "$melissa_id" "2003-06-08" "San Diego, CA")
olivia_family=$(create_family "$brandon_id" "$olivia_id" "2006-12-15" "Phoenix, AZ")
echo "✓ Created 12 Gen 3 families"

# Add divorce event to Ryan & Jessica (Gen 3) - they divorce after 8 years
create_event "$jessica_family" "" "divorce" "2010-11-15" "Miami, FL" "Divorce proceedings completed. Career conflicts and long-distance relationship issues."
echo "✓ Added divorce event to Ryan & Jessica Johnson"

echo ""

echo "📅 GENERATION 4 (1990s-2010s) - The Great-Grandchildren"
# Thomas & Amanda have 3 children
echo "Creating children of Gen 3 families..."
ethan_id=$(create_person "Ethan" "Smith" "M" "1991-05-12" "" "Boston, MA" "" "Recent college graduate. Works in digital marketing. Passionate about environmental activism and rock climbing.")
emma_id=$(create_person "Emma" "Smith" "F" "1993-08-20" "" "Boston, MA" "" "Graduate student studying marine biology. Scuba diving instructor. Dreams of working to protect coral reefs.")
noah_id=$(create_person "Noah" "Smith" "M" "1996-11-15" "" "Boston, MA" "")
add_child "$thomas_family" "$ethan_id"
add_child "$thomas_family" "$emma_id"
add_child "$thomas_family" "$noah_id"

# Kevin & Sarah have 2 children
ava_id=$(create_person "Ava" "Anderson" "F" "1993-07-08" "" "New York, NY" "")
liam_id=$(create_person "Liam" "Anderson" "M" "1996-03-25" "" "New York, NY" "")
add_child "$sarah_family" "$ava_id"
add_child "$sarah_family" "$liam_id"

# Daniel & Lisa have 4 children
isabella_id=$(create_person "Isabella" "Smith" "F" "1996-09-14" "" "Boston, MA" "" "Medical student following in great-grandfather Robert's footsteps. Volunteers at community health clinics.")
mason_id=$(create_person "Mason" "Smith" "M" "1998-12-20" "" "Boston, MA" "")
mia_id=$(create_person "Mia" "Smith" "F" "2001-04-18" "" "Boston, MA" "" "College student majoring in computer science. Develops mobile apps in her spare time. Gaming enthusiast.")
lucas_id=$(create_person "Lucas" "Smith" "M" "2003-07-22" "" "Boston, MA" "")
add_child "$daniel_family" "$isabella_id"
add_child "$daniel_family" "$mason_id"
add_child "$daniel_family" "$mia_id"
add_child "$daniel_family" "$lucas_id"

# Brian & Jennifer have 2 children
charlotte_id=$(create_person "Charlotte" "Harris" "F" "1997-06-10" "" "Seattle, WA" "")
oliver_id=$(create_person "Oliver" "Harris" "M" "2000-09-15" "" "Seattle, WA" "")
add_child "$jennifer2_family" "$charlotte_id"
add_child "$jennifer2_family" "$oliver_id"

# Christopher & Rachel have 3 children
amelia_id=$(create_person "Amelia" "Smith" "F" "1999-04-22" "" "Portland, OR" "")
benjamin_id=$(create_person "Benjamin" "Smith" "M" "2001-08-30" "" "Portland, OR" "")
harper_id=$(create_person "Harper" "Smith" "F" "2004-12-12" "" "Portland, OR" "")
add_child "$christopher_family" "$amelia_id"
add_child "$christopher_family" "$benjamin_id"
add_child "$christopher_family" "$harper_id"

# Mark & Emily have 2 children
evelyn_id=$(create_person "Evelyn" "Clark" "F" "1998-03-18" "" "Austin, TX" "")
jackson_id=$(create_person "Jackson" "Clark" "M" "2001-07-25" "" "Austin, TX" "")
add_child "$emily_family" "$evelyn_id"
add_child "$emily_family" "$jackson_id"

# Matthew & Ashley have 3 children
abigail_id=$(create_person "Abigail" "Johnson" "F" "2001-05-20" "" "Denver, CO" "")
aiden_id=$(create_person "Aiden" "Johnson" "M" "2003-09-10" "" "Denver, CO" "")
ella_id=$(create_person "Ella" "Johnson" "F" "2006-11-28" "" "Denver, CO" "")
add_child "$matthew_family" "$abigail_id"
add_child "$matthew_family" "$aiden_id"
add_child "$matthew_family" "$ella_id"

# Ryan & Jessica have 2 children
henry_id=$(create_person "Henry" "Walker" "M" "2003-02-14" "" "Miami, FL" "")
grace_id=$(create_person "Grace" "Walker" "F" "2005-06-18" "" "Miami, FL" "")
add_child "$jessica_family" "$henry_id"
add_child "$jessica_family" "$grace_id"

# Andrew & Nicole have 4 children
scarlett_id=$(create_person "Scarlett" "Johnson" "F" "2006-08-22" "" "Atlanta, GA" "")
sebastian_id=$(create_person "Sebastian" "Johnson" "M" "2008-10-30" "" "Atlanta, GA" "")
chloe_id=$(create_person "Chloe" "Johnson" "F" "2010-12-15" "" "Atlanta, GA" "")
logan_id=$(create_person "Logan" "Johnson" "M" "2013-03-20" "" "Atlanta, GA" "")
add_child "$andrew_family" "$scarlett_id"
add_child "$andrew_family" "$sebastian_id"
add_child "$andrew_family" "$chloe_id"
add_child "$andrew_family" "$logan_id"

# Jason & Sophia have 3 children
aria_id=$(create_person "Aria" "Young" "F" "2000-11-08" "" "Los Angeles, CA" "")
wyatt_id=$(create_person "Wyatt" "Young" "M" "2003-01-25" "" "Los Angeles, CA" "")
lily_id=$(create_person "Lily" "Young" "F" "2006-05-12" "" "Los Angeles, CA" "")
add_child "$sophia_family" "$aria_id"
add_child "$sophia_family" "$wyatt_id"
add_child "$sophia_family" "$lily_id"

# Alexander & Melissa have 2 children
zoey_id=$(create_person "Zoey" "Martinez" "F" "2004-07-18" "" "San Diego, CA" "")
elijah_id=$(create_person "Elijah" "Martinez" "M" "2007-09-22" "" "San Diego, CA" "")
add_child "$alexander_family" "$zoey_id"
add_child "$alexander_family" "$elijah_id"

# Brandon & Olivia have 3 children
avery_id=$(create_person "Avery" "Wright" "F" "2007-04-10" "" "Phoenix, AZ" "")
carter_id=$(create_person "Carter" "Wright" "M" "2009-08-15" "" "Phoenix, AZ" "")
madison_id=$(create_person "Madison" "Wright" "F" "2012-11-20" "" "Phoenix, AZ" "")
add_child "$olivia_family" "$avery_id"
add_child "$olivia_family" "$carter_id"
add_child "$olivia_family" "$madison_id"
echo "✓ Added 33 children to Gen 3 (total Gen 4)"
echo ""

echo "📅 GENERATION 5 (2010s-2020s) - The Great-Great-Grandchildren"
# Only the older Gen 4 members have children
echo "Creating Gen 5 (youngest generation)..."

# Ethan Smith has 2 children (with spouse)
hannah_id=$(create_person "Hannah" "Green" "F" "1992-03-15" "" "Boston, MA" "Graphic Designer" "Freelance designer specializing in brand identity. Passionate about sustainable fashion and eco-friendly design.")
ethan_family=$(create_family "$ethan_id" "$hannah_id" "2014-06-20" "Boston, MA")
jack_id=$(create_person "Jack" "Smith" "M" "2015-08-12" "" "Boston, MA" "" "Elementary school student. Loves dinosaurs and building with Lego. Takes piano lessons like his great-great-uncle Andrew.")
sophie_id=$(create_person "Sophie" "Smith" "F" "2018-10-25" "" "Boston, MA" "" "Kindergarten student. Enjoys painting and storytelling. Already showing artistic talent like her great-aunt Emily.")
add_child "$ethan_family" "$jack_id"
add_child "$ethan_family" "$sophie_id"

# Emma Smith has 1 child (with spouse)
james2_id=$(create_person "James" "Miller" "M" "1992-09-20" "" "Boston, MA" "Architect")
emma_family=$(create_family "$james2_id" "$emma_id" "2016-05-14" "Boston, MA")
oliver2_id=$(create_person "Oliver" "Miller" "M" "2017-07-18" "" "Boston, MA" "")
add_child "$emma_family" "$oliver2_id"

# Ava Anderson has 2 children (with spouse)
william2_id=$(create_person "William" "Rodriguez" "M" "1993-11-10" "" "New York, NY" "Software Developer")
ava_family=$(create_family "$william2_id" "$ava_id" "2015-09-08" "New York, NY")
mila_id=$(create_person "Mila" "Rodriguez" "F" "2016-12-20" "" "New York, NY" "")
leo_id=$(create_person "Leo" "Rodriguez" "M" "2019-04-15" "" "New York, NY" "")
add_child "$ava_family" "$mila_id"
add_child "$ava_family" "$leo_id"

# Isabella Smith has 3 children (with spouse)
daniel2_id=$(create_person "Daniel" "Scott" "M" "1995-06-18" "" "Boston, MA" "Business Analyst" "Data analytics specialist. Marathon runner and fitness enthusiast. Mentors young professionals in tech.")
isabella_family=$(create_family "$daniel2_id" "$isabella_id" "2017-08-22" "Boston, MA")
aurora_id=$(create_person "Aurora" "Scott" "F" "2018-11-10" "" "Boston, MA" "" "Preschooler who loves animals. Wants to be a veterinarian like her great-aunt Olivia. Has two pet rabbits.")
finn_id=$(create_person "Finn" "Scott" "M" "2020-03-25" "" "Boston, MA" "" "Toddler with boundless energy. Enjoys playing with trucks and trains. Learning to swim.")
luna_id=$(create_person "Luna" "Scott" "F" "2022-09-08" "" "Boston, MA" "" "The youngest member of the Smith family. Born during the pandemic. Happy and curious baby.")
add_child "$isabella_family" "$aurora_id"
add_child "$isabella_family" "$finn_id"
add_child "$isabella_family" "$luna_id"

# Charlotte Harris has 1 child (with spouse)
joseph_id=$(create_person "Joseph" "Baker" "M" "1996-04-12" "" "Seattle, WA" "Engineer")
charlotte_family=$(create_family "$joseph_id" "$charlotte_id" "2019-06-15" "Seattle, WA")
stella_id=$(create_person "Stella" "Baker" "F" "2020-08-20" "" "Seattle, WA" "")
add_child "$charlotte_family" "$stella_id"

# Add divorce event to Joseph & Charlotte (Gen 4) - they divorce after 3 years
create_event "$charlotte_family" "" "divorce" "2022-09-10" "Seattle, WA" "Divorce finalized. Different life goals and career priorities."
echo "✓ Added divorce event to Joseph & Charlotte Baker"

# Evelyn Clark has 2 children (with spouse)
nathan_id=$(create_person "Nathan" "Adams" "M" "1997-08-22" "" "Austin, TX" "Marketing Specialist")
evelyn_family=$(create_family "$nathan_id" "$evelyn_id" "2018-10-30" "Austin, TX")
hazel_id=$(create_person "Hazel" "Adams" "F" "2019-12-15" "" "Austin, TX" "")
max_id=$(create_person "Max" "Adams" "M" "2022-05-20" "" "Austin, TX" "")
add_child "$evelyn_family" "$hazel_id"
add_child "$evelyn_family" "$max_id"

# Aria Young has 1 child (with spouse)
samuel_id=$(create_person "Samuel" "Turner" "M" "2000-02-28" "" "Los Angeles, CA" "Photographer")
aria_family=$(create_family "$samuel_id" "$aria_id" "2020-07-18" "Los Angeles, CA")
nova_id=$(create_person "Nova" "Turner" "F" "2021-09-22" "" "Los Angeles, CA" "")
add_child "$aria_family" "$nova_id"

echo "✓ Added 12 children to Gen 4 (total Gen 5)"
echo ""

# Add some personal events to make the family tree more interesting
echo "📅 Adding personal events..."

# Add birth events for some key family members
create_event "" "$william_id" "birth" "1920-03-15" "Boston, MA" "Born during the Roaring Twenties"
create_event "" "$margaret_id" "birth" "1922-07-22" "Boston, MA" "Born during the Jazz Age"
create_event "" "$james_id" "birth" "1942-04-10" "Boston, MA" "Born during World War II"
create_event "" "$emily_id" "birth" "1973-07-12" "Chicago, IL" "Born during the Watergate era"

# Add death events for the deceased
create_event "" "$william_id" "death" "1995-12-10" "Boston, MA" "Passed away peacefully at home surrounded by family"
create_event "" "$margaret_id" "death" "2000-05-18" "Boston, MA" "Died of natural causes at age 77"

# Add some occupation events
create_event "" "$william_id" "occupation" "1950-01-01" "Boston, MA" "Founded Smith Construction Company"
create_event "" "$james_id" "occupation" "1968-06-01" "Boston, MA" "Graduated from Harvard Law School"
create_event "" "$emily_id" "occupation" "1995-05-15" "Chicago, IL" "First art exhibition at Chicago Gallery"

echo "✓ Added personal events (birth, death, occupation)"

echo ""
echo "✅ Family tree generation complete!"
echo ""
echo "📊 SUMMARY:"
echo "  Generation 1: 2 people (1 couple)"
echo "  Generation 2: 8 people (4 children + 4 spouses)"
echo "  Generation 3: 24 people (12 children + 12 spouses)"
echo "  Generation 4: 40 people (33 children + 7 spouses)"
echo "  Generation 5: 14 people (12 children + 2 spouses are parents from Gen 4)"
echo "  ─────────────────────────────"
echo "  TOTAL: 88 people across 5 generations"
echo ""
echo "💔 DIVORCE EVENTS ADDED:"
echo "  • James Smith & Jennifer Davis (Gen 2) - Divorced 1985"
echo "  • Ryan Walker & Jessica Johnson (Gen 3) - Divorced 2010"
echo "  • Joseph Baker & Charlotte Harris (Gen 4) - Divorced 2022"
echo ""
echo "🔗 Root Family ID: $gen1_family"
echo "   (William Smith & Margaret Brown)"
echo ""
echo "🌐 View the family tree at:"
echo "   http://localhost:5173/family/$gen1_family"

