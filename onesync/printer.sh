print_time() {
    date +"Current time: %T"
}

# Check if the user provided the duration as an argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <duration_in_seconds>"
    exit 1
fi

# Read the duration from the first argument
duration="$1"

# Validate if the duration is a positive integer
if ! [[ "$duration" =~ ^[1-9][0-9]*$ ]]; then
    echo "Invalid duration. Please provide a positive integer as the duration."
    exit 1
fi

# Start the loop to print the time every second
for (( i = 0; i < duration; i++ )); do
    print_time
    sleep 1
done