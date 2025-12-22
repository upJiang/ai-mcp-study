process.stdin.on('data', (data) => {
    const res = `回复: ${data.toString()}`;
    process.stdout.write(res);
});