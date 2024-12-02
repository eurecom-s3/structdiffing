/* v5.16.0 connector.h */
struct cn_dev {
	struct cb_id id;

	u32 seq, groups;
	struct sock *nls;

	struct cn_queue_dev *cbdev;
};