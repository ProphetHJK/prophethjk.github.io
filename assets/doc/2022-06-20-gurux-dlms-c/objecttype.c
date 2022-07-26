int CompareAndSwap(int *address, int expected, int new)
{
    if (*address == expected)
    {
        *address = new;
        return 1; // success
    }
    return 0; // failure
}
void AtomicIncrement(int *value, int amount)
{
    do
    {
        int old = *value;
    } while (CompareAndSwap(value, old, old + amount) == 0);
}
void insert(int value)
{
    node_t *n = malloc(sizeof(node_t));
    assert(n != NULL);
    n->value = value;
    n->next = head;
    head = n;
}
void insert(int value)
{
    node_t *n = malloc(sizeof(node_t));
    assert(n != NULL);
    n->value = value;
    lock(listlock); // begin critical section
    n->next = head;
    head = n;
    unlock(listlock); // end of critical section
}
void insert(int value)
{
    node_t *n = malloc(sizeof(node_t));
    assert(n != NULL);
    n->value = value;
    do
    {
        n->next = head;
    } while (CompareAndSwap(&head, n->next, n) == 0);
}