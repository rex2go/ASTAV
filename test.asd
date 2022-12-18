name text
age number
has_pet text
which_pet text ensure(~has_pet, "Ja") expect(["Hund", "Katze"]) or ensure(~has_pet, "Nein") expect(["Keins"])