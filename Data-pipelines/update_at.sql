-- Add the updated_at column
ALTER TABLE your_table_name
ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Create a function to update the timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger that uses the function
CREATE TRIGGER update_your_table_name_modtime
BEFORE UPDATE ON your_table_name
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();
